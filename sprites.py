import random
import pygame
import others
from others import is_collide_with_speed, TILED_MAP_DIR
import pytmx
import os
import sys

# В чем смысл id: в tiled комнаты есть отдельный слой, где как раз хранятся особенные плитки - флажки.
# Так как это плитка, следовательно, у неё есть id.
# Какие есть id и что они означают: об id написано в классах, где используют их


torch_group = pygame.sprite.Group()  # группа свечей
heal_group = pygame.sprite.Group()


def load_image_textures(name, colorkey=None):
    fullname = os.path.join('textures', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Player(pygame.sprite.Sprite):
    """Класс Player. Создается игрок"""  # Я больше ничего не мог придумать, чтобы объяснить, что такое Player
    image = load_image_textures('Adventurer\\adventurer_stand_prob_0.png',
                                -1)  # Изначальное изображение. Нужен для коллизии
    image = pygame.transform.scale(load_image_textures('Adventurer\\adventurer_stand_prob_0.png',
                                                       -1), (30, image.get_rect().height * 2.3))
    images_stand = [load_image_textures(f'Adventurer\\adventurer_stand_prob_{i}.png', -1)
                    for i in range(13)]  # спрайты игрока, когда он стоит
    images_move = [load_image_textures(f'Adventurer\\adventurer_move_prob_{i}.png', -1)
                   for i in range(8)]  # спрайты игрока, когда он двигается

    def __init__(self):
        super(Player, self).__init__()
        self.images_stand = [pygame.transform.scale(i, (30, self.image.get_height())) for i in self.images_stand]
        self.images_move = [pygame.transform.scale(i, (30, self.image.get_height())) for i in self.images_move]
        self.rect = self.image.get_rect()
        self.rect.x = self.x = others.WIDTH // 2
        self.rect.y = self.y = others.HEIGHT // 2
        image = pygame.transform.scale(self.image,
                                       (30, self.image.get_rect().height - self.rect.height // 1.01))
        self.mask = pygame.mask.from_surface(image)  # маска нужна для коллизии с бочками
        # Зачем нужен новый image с изменёнными параметрами: в маске будет храниться изображение, можно сказать, ног
        self.cnt = 0  # счетчик для изменения спрайтов
        self.step = 10  # именно настолько увеличивается self.cnt
        self.is_moving = False  # он идет или нет? Вот в чем вопрос
        self.left_right = 1  # взгляд направо - 1, взгляд налево - 0

    def draw(self, screen):
        """Метод класса. Отрисовка игрока"""
        if self.is_moving:
            screen.blit(self.images_move[self.cnt // self.step], self.rect)
        else:
            screen.blit(self.images_stand[self.cnt // self.step], self.rect)

    def move(self, x, y):
        """Метод класса. Движение игрока"""
        self.rect.x = self.x = others.WIDTH // 2 - self.rect.width // 2  # он всегда остаётся в центре(внимания) экрана
        self.rect.y = self.y = others.HEIGHT // 2 - self.rect.height // 2
        if (x or y) and not self.is_moving:  # если он начинает движение, но до этого стоял
            self.cnt = 0
            self.is_moving = True
        elif (x or y) and self.is_moving:  # если он двигается
            self.cnt += -self.cnt if self.cnt >= self.step * (len(self.images_move) - 1) else 1
        elif not (x or y) and self.is_moving:  # если он начинает стоять, но до этого двигался
            self.is_moving = False
            self.cnt = 0
        elif not (x or y) and not self.is_moving:  # если он стоит
            self.cnt += -self.cnt if self.cnt >= self.step * (len(self.images_stand) - 1) else 1
        self.set_left_right()

    def set_left_right(self):
        """Метод класса. Определяет взгляд игрока относительно мышки пользователя"""
        # решил сделать так: мышка на левой стороне экрана игры - персонаж смотрит налево и даже когда идет направо;
        # мышка на правой стороне экрана игры - персонаж смотрит направо и даже когда идет налево
        # Лучше будет, если персонаж идет назад и стреляет впереди себя, а не идет прямо и стреляет куда-то позади себя
        x, y = pygame.mouse.get_pos()
        if x >= others.WIDTH // 2 and not self.left_right:
            self.left_right = 1
            self.images_move = [pygame.transform.flip(i, True, False) for i in self.images_move]
            self.images_stand = [pygame.transform.flip(i, True, False) for i in self.images_stand]
        elif x < others.WIDTH // 2 and self.left_right:
            self.left_right = 0
            self.images_move = [pygame.transform.flip(i, True, False) for i in self.images_move]
            self.images_stand = [pygame.transform.flip(i, True, False) for i in self.images_stand]


class Monster(pygame.sprite.Sprite):
    """Класс Monster. Создается монстра"""
    image = load_image_textures('Monsters\\monster.png', -1)  # Изначальное изображение. Нужен для коллизии
    image = pygame.transform.scale(image, (image.get_rect().width * 2, image.get_rect().height * 2.3))

    def __init__(self, x, y):
        super(Monster, self).__init__()

        self.rect = self.image.get_rect()
        self.rect.x = self.x = x
        self.rect.y = self.y = y
        image = pygame.transform.scale(self.image,
                                       (self.image.get_rect().width * 2,
                                        self.image.get_rect().height - self.rect.height // 1.01))
        self.mask = pygame.mask.from_surface(image)  # маска нужна для коллизии с бочками
        # Зачем нужен новый image с изменёнными параметрами: в маске будет храниться изображение, можно сказать, ног
        self.random_x = 0  # скорость, которая он выберет случайно
        self.random_y = 0
        self.delay = random.randrange(1, 11) * 30  # задержка между ходьбой
        self.is_moving = 0  # если он двигается

    def draw(self, screen):
        """Метод класса. Отрисовка монстра"""
        screen.blit(self.image, self.rect)

    def move(self, x, y):
        """Метод класса. Движение монстра относительно игрока"""
        self.rect.x -= x
        self.rect.y -= y

    def self_move(self):
        """Метод класса. Движение монстра вне зависимости игрока"""
        if self.delay - 1 == 0 and self.is_moving == 0:  # если задержка закончилась и он не двигается
            self.is_moving = random.randrange(1, 21)
            self.delay = 0
            self.random_x = random.randrange(-10, 11)
            self.random_y = random.randrange(-10, 11)
        elif self.delay == 0 and self.is_moving - 1 == 0:  # если задержка на нуле и он хочет заканчивать движение
            self.is_moving = 0
            self.delay = random.randrange(1, 11) * 30
            self.random_x = 0
            self.random_y = 0
        # Дальше не требуется комментариев
        elif self.delay != 0 and self.is_moving == 0:
            self.delay -= 1
        elif self.is_moving != 0 and self.delay == 0:
            self.is_moving -= 1
            self.rect.x += self.random_x
            self.rect.y += self.random_y

    def collide_with_wall(self, x, y, map_surface, layer, tile_size):
        """Метод класса. Коллизия между монстром и непроходимой стеной"""
        x = (self.rect.x + self.random_x - x + (
            self.rect.width if self.random_x >= 0 else 0)) // tile_size
        y = int(
            self.rect.y + self.rect.height // 1.01 + self.random_y - y + (
                (self.rect.height - self.rect.height // 1.1) if self.random_y >= 0 else 0)) \
            // tile_size
        # x и y - координаты относительно tiled комнаты.
        # Так как комнаты сделано в tiled editor map, следовательно, комнаты плиточные.
        # Тогда х и у - координаты плитки, на которой стоит монстр
        if -1 < x < map_surface.width and -1 < y < map_surface.height:
            image = map_surface.get_tile_image(x, y, layer)
            if image:
                self.random_x = 0
                self.random_y = 0


class Barrel(pygame.sprite.Sprite):
    """Класс Barrel. Создается бочка"""
    image = pygame.transform.scale(load_image_textures('barrel.png', -1), (28, 32))

    # id - 1260
    def __init__(self, x, y):
        super(Barrel, self).__init__()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

        self.probality = 5  # вероятность выпадение бутылки исцеления в проценте

    def draw(self, screen):
        """Метод класса. Отрисовка бочки"""
        screen.blit(self.image, self.rect)

    def move(self, x, y):
        """Метод класса. Движение бочки"""
        self.rect.x -= x
        self.rect.y -= y

    def is_collide(self, pers, x_speed, y_speed):
        """Метод класса. Коллизия между персонажем и бочкой"""
        pers.rect.y += pers.rect.height // 1.5  # здесь не нужно, чтобы голова персонажа была над бочкой по координате у
        self.rect.x -= x_speed
        if pygame.sprite.collide_mask(self, pers):  # вот где понадобилась маска
            self.rect.x += x_speed
            x_speed = 0
        else:
            self.rect.x += x_speed
        self.rect.y -= y_speed
        if pygame.sprite.collide_mask(self, pers):
            self.rect.y += y_speed
            y_speed = 0
        else:
            self.rect.y += y_speed
        pers.rect.y -= pers.rect.height // 1.5
        return x_speed, y_speed

    def kill(self):
        a = random.randrange(101)
        if a <= self.probality:
            Heal(self.rect.x, self.rect.y)
        super(Barrel, self).kill()


class Torch(pygame.sprite.Sprite):
    """Класс Torch. Создается свечка(или свечки) или костер"""

    # id:
    # 1375 - torch is_collising
    # 1440 - torch not is_collising
    # 488 - candleA is_collising
    # 552 - candleA not is_collising
    # 614 - candleB is_collising
    # 549 - candleB not is_collising
    # is_collising - с коллизией
    # некоторые стоят на столбах и у них не надо проверять коллизию
    def __init__(self, filename, x, y, is_collising):
        super(Torch, self).__init__()
        if is_collising:
            torch_group.add(self)  # эта группа проверяет коллизию.
            # Иначе попадает группу, которая находится в классе комнаты
        self.images = [pygame.transform.scale(load_image_textures(f'Catacombs\\{filename}{i}.png', -1),
                                              (32 if filename != 'candleA_0' else 16, 32))
                       for i in range(1, 5)]  # мешает filename для того, чтобы он был создан снаружи init
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.cnt = 0  # счетчик для изменения спрайтов
        self.step = 10  # именно настолько увеличивается self.cnt
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        """Метод класса. Отрисовка свечки(или свечек) или костра"""
        screen.blit(self.image, self.rect)
        self._increment_cnt()

    def move(self, x, y):
        """Метод класса. Движение свечки(или свечек) или костра"""
        self.rect.x -= x
        self.rect.y -= y

    def _increment_cnt(self):
        """Метод класса. Увеличивает self.cnt для анимации спрайта"""
        self.image = self.images[self.cnt // self.step]
        self.cnt += 1
        if self.cnt >= 40:
            self.cnt = 0

    def is_collide(self, pers, x_speed, y_speed):
        """Метод класса. Проверяет коллизию между персонажем и свечкой"""
        pers.rect.y += pers.rect.height // 1.01  # Мы смотрим коллизию по ногам, а не по телу
        self.rect.x -= x_speed
        if pygame.sprite.collide_mask(self, pers):  # вот где понадобилась маска
            self.rect.x += x_speed
            x_speed = 0
        else:
            self.rect.x += x_speed
        self.rect.y -= y_speed
        if pygame.sprite.collide_mask(self, pers):
            self.rect.y += y_speed
            y_speed = 0
        else:
            self.rect.y += y_speed
        pers.rect.y -= pers.rect.height // 1.01
        return x_speed, y_speed


class Gate:
    """Класс Gate. Создаются ворота"""

    def __init__(self, x, y, orientation, top_or_bottom=''):
        self.map = pytmx.load_pygame(TILED_MAP_DIR + f'\\{orientation}_gate.tmx')
        # Чтобы не делать два файла ворот разных размеров (6*3 и 6*4), решил сделать так:
        self.top = True if top_or_bottom == 'top' else False
        self.x = x
        self.y = y
        self.height = self.map.height + (1 if self.top else 0)  # посмотрите на северные ворота и на южные
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.orientation = orientation  # горизонтальный или вертикальный
        self.cnt = 0  # счетчик для изменения спрайтов
        self.step = 60 // self.height  # именно настолько увеличивается self.cnt

    def move(self, x, y):
        """Метод класса. Движение ворот"""
        self.x -= x
        self.y -= y

    def render(self, screen, is_stay_gates):
        """Метод класса. Отрисовка ворот"""
        t = False
        for y in range(self.height):
            for x in range(1 if self.orientation == 'horizontal' else 0,
                           self.width - (1 if self.orientation == 'horizontal' else 0)):
                for layer in range(len(self.map.layers)):
                    if self.top and y >= 2:  # отрисовка 3 строки ворот
                        image = self.map.get_tile_image(x, y - 1, layer)
                    else:
                        image = self.map.get_tile_image(x, y, layer)
                    if image:
                        if self.orientation == 'horizontal' and \
                                self.cnt // self.step == y:
                            image = pygame.transform.chop(image, [0,
                                                                  int(self.tile_size * (
                                                                          self.cnt % self.step) / self.step), 0,
                                                                  self.tile_size - int(self.tile_size * (
                                                                          self.cnt % self.step) / self.step)])
                            # chop для анимации
                            t = True
                        if self.orientation == 'horizontal':
                            screen.blit(image, (self.x + self.tile_size * x,
                                                self.y + self.tile_size * y - int(
                                                    self.tile_size * self.cnt / self.step) + self.tile_size *
                                                self.height))
                        else:
                            screen.blit(image, (self.x + self.tile_size * x,
                                                self.y + self.tile_size * y))

            if t:
                self._increment_step(is_stay_gates)
                return

    def _increment_step(self, is_stay_gates):
        """Метод класса. Увеличивает self.cnt для анимации спрайта"""
        self.cnt += 1 if is_stay_gates and self.cnt < 60 else 0

    def is_collide(self, player, x_speed, y_speed, is_stay_gates):
        """Метод класса. Проверяет коллизию между персонажем и воротами"""
        if is_stay_gates and any([x_speed, y_speed]):
            if self.orientation == 'vertical':
                for y in range(self.height):
                    image = self.map.get_tile_image(0, y, 0)
                    if image:
                        x_speed, y_speed = is_collide_with_speed(player, image, self.x, self.y + y * self.tile_size,
                                                                 x_speed, y_speed)
            elif self.orientation == 'horizontal':
                for x in range(self.width):
                    image = self.map.get_tile_image(x, 2, 0)
                    if image:
                        x_speed, y_speed = is_collide_with_speed(player, image, x * self.tile_size + self.x,
                                                                 (3 if self.top else 2) * self.tile_size + self.y,
                                                                 x_speed, y_speed)
        return x_speed, y_speed


class Spike(pygame.sprite.Sprite):
    """Класс Gate. Создаются шипы"""
    images = [pygame.transform.scale(load_image_textures(f'Catacombs\\spike_{i}.png', -1), (32, 32)) for i in range(5)]
    images.extend([pygame.transform.scale(load_image_textures(f'Catacombs\\spike_{i}.png', -1), (32, 32))
                   for i in range(4, -1, -1)])

    # id - 1196
    def __init__(self, x, y):
        super(Spike, self).__init__()
        self.image = self.images[0]  # изображение нужное для коллизии
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.cnt = 0  # счетчик для изменения спрайтов
        self.step = 10  # именно настолько увеличивается self.cnt
        self.mask = pygame.mask.from_surface(self.image)
        self.delay = 0

    def draw(self, screen):
        """Метод класса. Отрисовка шипов"""
        screen.blit(self.image, self.rect)

    def move(self, x, y):
        """Метод класса. Движение шипов"""
        self.rect.x -= x
        self.rect.y -= y

    def increment_cnt(self):
        """Метод класса. Увеличивает self.cnt для анимации спрайта"""
        if self.delay:
            self.delay -= 1
            return
        try:
            self.image = self.images[self.cnt // self.step]
        except IndexError:
            self.image = self.images[0]
        self.cnt += 1
        if self.cnt >= self.step * (len(self.images) - 1):
            self.cnt = 0
            self.image = self.images[0]
            self.delay = 60

    def is_collide(self, player, x_speed, y_speed):
        # пока в разработке
        pass


class Heal(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image_textures('heal.png', -1), (28, 32))

    def __init__(self, x, y):
        super(Heal, self).__init__(heal_group)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.cnt_heal = 20

    def move(self, x, y):
        """Метод класса. Движение бутылки исцеления"""
        self.rect.x -= x
        self.rect.y -= y

    def heal(self):
        print('heal')
        # сперва лечит игрока
        self.kill()
