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


import pygame
import math
import random
import ui
import pickle

PLAYER_RELOAD_EVENT = pygame.USEREVENT + 1
PLAYER_SHOOT_EVENT = pygame.USEREVENT + 2

all_sprites = pygame.sprite.Group()
entity_sprites = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()
gun_sprites = pygame.sprite.Group()
monster_sprites = pygame.sprite.Group()
collide_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
bar_sprites = pygame.sprite.Group()
dead_monsters = pygame.sprite.Group()
ui_sprites = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, center_pos=(0, 0), image=None, max_hp=100, inventory=None, hp_left=100, balance=0):
        super().__init__(all_sprites)
        self.add(player_group, entity_sprites)

        self.max_hp = max_hp
        self.hp_left = hp_left

        self.inventory_size = 3
        self.inventory = inventory
        self.active_gun = self.inventory[0]
        self.active_gun.add(gun_sprites, all_sprites, entity_sprites)

        self.cells = ui.Inventory(sprite_group=(all_sprites, ui_sprites))

        self.image = pygame.Surface((50, 50), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, (128, 0, 255), (0, 0, 50, 50), 0)

        self.rect.x = center_pos[0] - self.image.get_width() // 2
        self.rect.y = center_pos[1] - self.image.get_height() // 2

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

        self.balance = balance

    def take_damage(self, damage):
        self.hp_left -= damage

    def on_clicked(self, event):
        if event.button == 1:
            self.active_gun.try_shoot()

    def on_k_pressed(self, event):
        if event.key == pygame.K_g:
            self.drop_gun()
        if event.key == pygame.K_f:
            self.take_gun()

        if event.key == pygame.K_1:
            self.switch_gun(0)
        if event.key == pygame.K_2:
            self.switch_gun(1)
        if event.key == pygame.K_3:
            self.switch_gun(2)

    def take_gun(self):
        if self.inventory.count(None) > 0:
            for gun in gun_sprites:
                if pygame.sprite.spritecollide(gun, player_group, False):
                    if gun.can_be_raised and gun not in self.inventory:
                        gun.is_raised = True
                        gun.set_display(False)
                        for i, item in enumerate(self.inventory):
                            if item == None:
                                self.inventory[i] = gun
                                break
                        break
            self.cells.update()

    def drop_gun(self):
        if self.inventory.count(None) < 2:
            self.active_gun.is_raised = False
            self.active_gun.is_reloading_now = False
            pygame.time.set_timer(self.active_gun.reload_event, 0)
            self.active_gun.can_shoot = True
            pygame.time.set_timer(self.active_gun.shoot_event, 0)

            self.inventory.remove(self.active_gun)
            self.inventory.append(None)
            for item in self.inventory[::-1]:
                if item != None:
                    self.active_gun = item
            self.active_gun.set_display(True)
            self.cells.update()

    def switch_gun(self, n):
        if self.inventory[n] != None:
            self.active_gun.is_reloading_now = False
            pygame.time.set_timer(self.active_gun.reload_event, 0)
            self.active_gun.can_shoot = True
            pygame.time.set_timer(self.active_gun.shoot_event, 0)
            self.active_gun.set_display(False)
            self.active_gun = self.inventory[n]
            self.active_gun.set_display(True)
            self.active_gun.is_raised = True
            self.cells.update()

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.cord_y -= 80 / 60
        if keys[pygame.K_a]:
            self.cord_x -= 80 / 60
        if keys[pygame.K_s]:
            self.cord_y += 80 / 60
        if keys[pygame.K_d]:
            self.cord_x += 80 / 60

    def give_money(self, reward):
        self.balance += reward

    def update(self):
        self.rect.x = self.cord_x
        self.rect.y = self.cord_y


class Gun(pygame.sprite.Sprite):
    # damage_type: point, splash
    def __init__(self, is_raised=False, target_group=monster_sprites, name='gun', can_be_raised=True, center_pos=(0, 0),
                 image=None, destroy_bullets=True, damage_type='point', bullet_image=None, bullet_color=(128, 128, 128), \
                 bullet_size=(10, 10), bullet_speed=300, fire_rate=300, shooting_accuracy=1, damage=0, splash_damage=10,
                 splash_radius=150, ammo=10, \
                 reload_time=3000):

        super().__init__()
        self.add(gun_sprites, all_sprites, entity_sprites)

        self.target_group = target_group
        self.name = name

        # Их не изменять
        self.center_pos = center_pos
        self.destroy_bullets = destroy_bullets
        self.bullet_color = bullet_color
        self.bullet_image = bullet_image
        self.bullet_size = bullet_size
        self.bullet_speed = bullet_speed
        self.damage_type = damage_type
        self.damage = damage
        self.splash_damage = splash_damage
        self.splash_radius = splash_radius
        self.ammo = ammo
        self.fire_rate = fire_rate
        self.shooting_accuracy = shooting_accuracy

        self.ammo_amount = self.ammo
        self.reload_time = reload_time

        self.reload_event = PLAYER_RELOAD_EVENT
        self.shoot_event = PLAYER_SHOOT_EVENT

        self.original_image = image
        if image == None:
            self.image = pygame.Surface((25, 25), pygame.SRCALPHA, 32)
            pygame.draw.rect(self.image, self.bullet_color, (0, 0, 25, 25), 0)
        else:
            self.image = pygame.transform.scale(image, (image.get_width() * 2, image.get_height() * 2))

        self.rotate_image = self.image
        self.rect = self.image.get_rect(center=center_pos)

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

        self.can_be_raised = can_be_raised
        self.is_displayed = True
        self.is_raised = False or is_raised
        self.is_reloading_now = False
        self.can_shoot = True

    def set_display(self, bool):
        if bool:
            self.is_displayed = True
            self.add(gun_sprites, all_sprites, entity_sprites)
        else:
            self.is_displayed = False
            all_sprites.remove(self)

    def try_shoot(self):
        if self.can_shoot:
            self.shoot(target_pos=pygame.mouse.get_pos())
            self.can_shoot = False
            pygame.time.set_timer(self.shoot_event, self.fire_rate)

    def shoot(self, target_pos):
        if not self.is_reloading_now:
            if self.ammo_amount != 0:
                self.ammo_amount -= 1
                Bullet(self, target_pos)
            else:
                self.is_reloading_now = True
                pygame.time.set_timer(self.reload_event, self.reload_time)

    def reload_ammo(self):
        self.is_reloading_now = False
        self.ammo_amount += self.ammo

    def rotate(self, target):
        if self.math_angle(target) < 0:
            self.image = pygame.transform.flip(
                pygame.transform.rotate(self.rotate_image, -self.math_angle(target) + 90), False, True)
        else:
            self.image = pygame.transform.rotate(self.rotate_image, self.math_angle(target) - 90)

    def math_angle(self, target):
        rel_x, rel_y = target[0] - self.cord_x - \
                       self.rotate_image.get_width() / 2, target[1] - \
                       self.cord_y - self.rotate_image.get_height() / 2
        angle = (180 / math.pi) * math.atan2(rel_x, rel_y)
        return angle

    def copy(self):
        return Gun(target_group=monster_sprites, can_be_raised=self.can_be_raised, name=self.name,
                   center_pos=self.center_pos, image=self.original_image, destroy_bullets=self.destroy_bullets, \
                   damage_type=self.damage_type, bullet_image=None, bullet_color=self.bullet_color,
                   bullet_size=self.bullet_size, bullet_speed=self.bullet_speed, \
                   fire_rate=self.fire_rate, shooting_accuracy=self.shooting_accuracy, damage=self.damage,
                   splash_damage=self.splash_damage, \
                   splash_radius=self.splash_radius, ammo=self.ammo, reload_time=self.reload_time)

    def update(self):
        self.rect.x = self.cord_x
        self.rect.y = self.cord_y

        if self.is_raised:
            self.cord_x = player_group.sprite.cord_x + 30
            self.cord_y = player_group.sprite.cord_y + 20

            self.rotate(target=pygame.mouse.get_pos())


class Shotgun(Gun):
    def __init__(self, is_raised=False, target_group=monster_sprites, name='gun', \
                 can_be_raised=True, center_pos=(0, 0), image=None, destroy_bullets=True, damage_type='point', \
                 bullet_image=None, bullet_color=(128, 128, 128), bullet_size=(10, 10), bullet_speed=300, \
                 fire_rate=300, shooting_accuracy=1, damage=0, splash_damage=10, splash_radius=150, ammo=10,
                 reload_time=3000):
        super().__init__(is_raised, target_group, name, can_be_raised, center_pos, image, destroy_bullets, \
                         damage_type, bullet_image, bullet_color, bullet_size, bullet_speed, fire_rate,
                         shooting_accuracy, \
                         damage, splash_damage, splash_radius, ammo, reload_time)

    def shoot(self, target_pos):
        if not self.is_reloading_now:
            if self.ammo_amount != 0:
                self.ammo_amount -= 1
                for _ in range(5):
                    self.bullet_speed = random.randint(250, 350)
                    Bullet(self, target_pos)
            else:
                self.is_reloading_now = True
                pygame.time.set_timer(self.reload_event, self.reload_time)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, gun, cords_to=(0, 0)):
        super().__init__(all_sprites)
        self.add(bullet_group, entity_sprites)

        self.gun = gun
        self.target_group = self.gun.target_group
        self.cords_to = cords_to
        self.cords_from = (self.gun.rect.centerx, self.gun.rect.centery)

        self.cords = [self.cords_from[0], self.cords_from[1]]

        if self.gun.bullet_image == None:
            self.image = pygame.Surface((self.gun.bullet_size[0], self.gun.bullet_size[1]), pygame.SRCALPHA, 32)
            pygame.draw.rect(self.image, self.gun.bullet_color,
                             (0, 0, self.gun.bullet_size[0], self.gun.bullet_size[1]), 0)
        else:
            self.image = self.gun.bullet_image
        self.rect = self.image.get_rect()
        self.rect.x = self.cords_from[0]
        self.rect.y = self.cords_from[1]

        self.vx, self.vy = self.math_speed()
        self.rotate()

    def math_angle(self):
        rel_x, rel_y = self.randomized_mouse_cord_x - self.rect.x - \
                       self.gun.bullet_size[0] / 2, self.randomized_mouse_cord_y - \
                       self.rect.y - self.gun.bullet_size[1] / 2
        angle = (180 / math.pi) * math.atan2(rel_x, rel_y)
        return angle

    def rotate(self):
        self.image = pygame.transform.rotate(self.image, self.math_angle())

    def math_speed(self):
        self.randomized_mouse_cord_x = self.cords_to[0] + random.choice([-1, 1]) * \
                                       random.uniform(0, (1 - self.gun.shooting_accuracy)) * self.cords_to[0]

        self.randomized_mouse_cord_y = self.cords_to[1] + random.choice([-1, 1]) * \
                                       random.uniform(0, (1 - self.gun.shooting_accuracy)) * self.cords_to[1]

        rel_x = self.randomized_mouse_cord_x - self.cords_from[0] - self.image.get_width() / 2
        rel_y = self.randomized_mouse_cord_y - self.cords_from[1] - self.image.get_height() / 2

        vx = round(rel_x / math.sqrt(rel_x ** 2 + rel_y ** 2) * self.gun.bullet_speed, 2)
        vy = round(rel_y / math.sqrt(rel_x ** 2 + rel_y ** 2) * self.gun.bullet_speed, 2)
        return (vx, vy)

    def move(self):
        self.cords[0] += self.vx / 60
        self.cords[1] += self.vy / 60

    def collision_handling(self):
        sprite_collided = pygame.sprite.spritecollide(self, self.target_group, False)
        if sprite_collided:
            sprite_collided = sprite_collided[0]
            if self.gun.destroy_bullets:
                self.kill()

            sprite_collided.hp_left -= self.gun.damage

            if self.gun.damage_type == 'splash':
                self.splash_damage(sprite_collided)

    def splash_damage(self, sprite):
        splash = pygame.sprite.Sprite()
        splash.image = pygame.Surface((self.gun.splash_radius, self.gun.splash_radius), pygame.SRCALPHA, 32)
        splash.rect = splash.image.get_rect(center=(self.rect.centerx, self.rect.centery))
        for target in self.gun.target_group:
            if target != sprite:
                if (self.rect.centerx - target.rect.centerx) ** 2 + (
                        self.rect.centery - target.rect.centery) ** 2 < self.gun.splash_radius ** 2:
                    target.hp_left -= self.gun.splash_damage

    def optimize(self):
        if not 0 < self.cords[0] < 800 or \
                not 0 < self.cords[1] < 500:
            self.kill()

    def update(self):
        self.move()

        self.rect.x = self.cords[0]
        self.rect.y = self.cords[1]

        self.optimize()
        self.collision_handling()


class Monster(pygame.sprite.Sprite):
    def __init__(self, center_pos, image, hp=100, reward=1, attack_range=200, gun=None, dead=False, running_speed=50,
                 player_avoidance=True, move_randomly=True):
        super().__init__(all_sprites)
        self.add(monster_sprites, collide_group, entity_sprites)

        if gun == None:
            self.active_gun = Gun(name='bad pistol', damage=0, can_be_raised=False, bullet_color=(
            random.randint(96, 196), random.randint(96, 196), random.randint(96, 196)), fire_rate=1000, ammo=-1,
                                  shooting_accuracy=0.9, target_group=player_group)
        else:
            self.active_gun = gun
        self.active_gun.damage = 0
        self.active_gun.can_be_raised = False
        self.active_gun.ammo = -1
        self.active_gun.target_group = player_group
        self.active_gun.add(all_sprites, gun_sprites)

        self.player_avoidance = player_avoidance
        self.attack_range = attack_range
        self.running_speed = running_speed
        self.max_hp = hp
        self.reward = reward
        self.hp_left = self.max_hp

        self.hp_bar = Bars(owner=self, max_hp=self.max_hp)

        self.image = image
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 3, self.image.get_height() * 3))
        self.rect = self.image.get_rect(center=center_pos)

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

        self.shooting_timer = random.randint(0, 30)
        self.movement_timer = 20
        self.movement_direction = 1
        self.move_randomly = move_randomly

        if dead:
            self.die()

    def respawn(self):
        self.hp_left = self.max_hp
        self.add(all_sprites, collide_group, monster_sprites, entity_sprites)
        dead_monsters.remove(self)
        self.hp_bar.add(all_sprites, bar_sprites)
        self.active_gun.add(all_sprites, gun_sprites)

    def die(self):
        self.hp_left = 0
        self.kill()
        self.add(dead_monsters)

    def give_reward(self):
        player_group.sprite.give_money(self.reward)

    def shoot(self):
        if self.shooting_timer > 0:
            if random.randint(0, 4) == 0:
                self.shooting_timer -= 1
        else:
            self.active_gun.shoot((player_group.sprite.rect.centerx, player_group.sprite.rect.centery))
            self.shooting_timer = 10

    def walk(self, movement_direction=1, random_direction=1):
        distance = max(math.sqrt((self.rect.centerx - player_group.sprite.rect.centerx) ** 2 + (
                    self.rect.centery - player_group.sprite.rect.centery) ** 2), 1)
        vx = (self.rect.centerx - player_group.sprite.rect.centerx) / distance / 60 * self.running_speed
        vy = (self.rect.centery - player_group.sprite.rect.centery) / distance / 60 * self.running_speed

        self.cord_x -= movement_direction * vx * random_direction
        self.cord_y -= movement_direction * vy * random_direction

    def run_away(self):
        if self.player_avoidance:
            if self.current_distance_sqr < self.attack_range ** 2 / 3:
                self.walk(movement_direction=-1)

    def distance_check(self):
        self.current_distance_sqr = (self.rect.centerx - player_group.sprite.rect.centerx) ** 2 + (
                    self.rect.centery - player_group.sprite.rect.centery) ** 2
        if self.current_distance_sqr < (self.attack_range + 100) ** 2:
            self.shoot()

        if self.current_distance_sqr < self.attack_range ** 2:
            self.run_away()
        else:
            self.walk()

        self.random_movement()

    def random_movement(self):
        if self.move_randomly:
            if self.movement_timer > 0:
                if random.randint(0, 15) == 0:
                    self.movement_timer -= 1
            else:
                self.movement_direction = self.movement_direction * -1
                self.movement_timer = 10
            self.walk(random_direction=self.movement_direction / 2)

    def update(self):
        if self.hp_left <= 0:
            self.die()
            self.give_reward()
            self.active_gun.kill()
        else:
            self.rect.x = self.cord_x
            self.rect.y = self.cord_y

            self.active_gun.cord_x = self.rect.centerx
            self.active_gun.cord_y = self.rect.centery

            self.distance_check()
            self.active_gun.rotate(player_group.sprite.rect.center)


class Bars(pygame.sprite.Sprite):
    def __init__(self, owner, max_hp=100, bar_size=(30, 10), border_size=2, bar_color=(255, 0, 0), bg_color_1=(0, 0, 0),
                 bg_color_2=(128, 128, 128)):
        super().__init__(all_sprites)
        self.add(bar_sprites)

        self.owner = owner
        self.max_hp = max_hp
        self.bar_size = bar_size
        self.border_size = border_size
        self.bar_color = bar_color
        self.bg_color_1 = bg_color_1
        self.bg_color_2 = bg_color_2

        self.hp_left = self.max_hp

        self.image = pygame.Surface((self.bar_size[0], self.bar_size[1]), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()

    def update(self):
        if dead_monsters in self.owner.groups() or len(self.owner.groups()) == 0:
            self.kill()

        self.hp_left = self.owner.hp_left

        self.rect.x = self.owner.rect.centerx - self.bar_size[0] / 2
        self.rect.y = self.owner.cord_y - 20

        pygame.draw.rect(self.image, (64, 64, 64), (0, 0, self.bar_size[0], self.bar_size[1]), 0)
        pygame.draw.rect(self.image, (64, 0, 0), (self.border_size, self.border_size, self.bar_size[0] - \
                                                  2 * self.border_size, self.bar_size[1] - 2 * self.border_size), 0)
        pygame.draw.rect(self.image, (255, 64, 64), (self.border_size, self.border_size, (self.bar_size[0] - \
                                                                                          2 * self.border_size) * self.hp_left / self.max_hp,
                                                     self.bar_size[1] - 2 * self.border_size), 0)