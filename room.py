import random
import pygame
import pytmx
from others import TILED_MAP_DIR, PICTURE_WAllS, is_collide_with_speed, is_collide, BAR_SPIKE_MAP_DIR
import others
import sprites
from sprites import Gate, Barrel, Spike, Cell
import os

# комната 704*704
# протяженность коридора 512 - 32

# Ключевой момент: карта представляет собой квадрат 4*4, в котором комнаты случайно выбирают свои координаты.
# Следовательно, с учетом коридоров между ними карта получается с длиной около 4500 и такой шириной.
# Тогда размер 4500*4500.
# Координаты относительно квадрата 4*4 нужны только для комнат и коридоров.
# Другие классы используют координаты относительно этих же комнат за исключением немногих

is_stay_gates = True  # Стоят ли ворота. Если да, то ты значит с кем-то сражаешься; если нет, то значит ты свободен


class RoomCorridor:
    """Класс-родитель для класса Room или Corridor
    При инициализации принимает такие значение как:
    x - координата относительно квадрата 4*4
    y - координата относительно квадрата 4*4
    filename - имя файла комнаты или коридора"""

    def __init__(self, x, y, filename):

        self.map = pytmx.load_pygame(f'{TILED_MAP_DIR}\\{filename}.tmx')  # загрузка комнаты
        self.x = x * (704 + 512)
        self.y = y * (704 + 512)
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.filename_room = filename  # можно сказать, что здесь хранится не именно название файла,
        # а название самой комнаты
        self.picture_walls = dict()  # Рисунки на стене. Сделано так, чтобы были случайные рисунки в каждой комнате
        self.redrawing = True  # перерисовка игрока
        self.redrawing_monsters = []
        # redrawing нужен для создания 3D столбов. Проверить можно так: сперва стойте сзади столба, затем перед ним.
        # Потом ответьте на вопрос: что первым рисуется: столбы или персонажи?
        self.walls_gates = dict()  # Словарь. Нужен для того, чтобы определить, где стена, а где коридор с воротами
        self.torch_group = pygame.sprite.Group()  # свечи, которые стоят на столбах
        self.monster_group = pygame.sprite.Group()  # монстры в определенной комнате
        self.barrel_group = pygame.sprite.Group()
        self.spike_group = pygame.sprite.Group()

    def render(self, screen, x_speed, y_speed, player):
        """Метод класса. Рисует пол и стены, через которых нельзя пройти"""
        x_speed, y_speed = self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, range(1, 3),
                                           functions=[self.is_render_picture_walls, is_collide_with_speed],
                                           player=player, x_speed=x_speed,
                                           y_speed=y_speed)
        return x_speed, y_speed

    def render_passing_walls(self, screen, player):
        """Метод класса.
        Рисуются стены, через которые можно пройти, а также перерисовывает персонажей, если нужно"""
        self.redrawing = True
        self.redrawing_monsters = [i for i in self.monster_group]
        self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, [3],
                        functions=[self.redrawing_player],
                        player=player)
        [i.draw(screen) for i in self.torch_group]
        if self.redrawing:
            player.draw(screen)
        if self.redrawing_monsters:
            [i.draw(screen) for i in self.redrawing_monsters]

    def rect_in_screen(self, x, y, width_dec, height_dec):
        """Возвращает начальные и конечные координаты ячеек комнаты, которые попадают на экран"""
        # Без этой оптимизации процесс отрисовки был бы ОЧЕНЬ долгим и просаживался бы FPS
        x1 = 0 if max(0, x) == x else (-x // self.tile_size)
        x2 = width_dec if min(others.WIDTH, width_dec * self.tile_size + x) == width_dec * self.tile_size + x \
            else width_dec - (width_dec * self.tile_size + x - others.WIDTH) // self.tile_size
        y1 = 0 if max(0, y) == y else (-y // self.tile_size)
        y2 = height_dec if min(others.HEIGHT, height_dec * self.tile_size + y) == height_dec * self.tile_size + y \
            else height_dec - (height_dec * self.tile_size + y - others.HEIGHT) // self.tile_size
        return x1, y1, x2, y2

    def move(self, x, y):
        """Метод класса. Движение комнат с его объектами"""
        # Особенность движения объектов: двигается не персонаж(он все время стоит на месте относительно экрана),
        # а комнаты и другие объекты
        self.x -= x
        self.y -= y
        [i.move(x, y) for i in self.torch_group]
        [i.move(x, y) for i in self.monster_group]
        [i.move(x, y) for i in self.barrel_group]
        [i.move(x, y) for i in self.spike_group]

    def blit_tiles(self, screen, map_surface, x_pos, y_pos, width, height, layers, functions=[],
                   x_speed=None, y_speed=None, player=None, layers_collide=2):
        """Метод класса. Другими словами рендер
        Параметры:
        screen - основное окно экрана
        map_surface - tiled map
        x_pos - изначальная позиция объекта по координате x
        y_pos - изначальная позиция объекта по координате y
        width - длина tiled map
        height - ширина tiled map
        layers - слои, которые нужно рисовать
        function - список функции, которые использовать
        x_speed - скорость персонажа по координате x
        y_speed - скорость персонажа по координате y
        player - класс игрока
        layers_collide - слои, которые нужно проверить на коллизию объектов
        """
        x1, y1, x2, y2 = self.rect_in_screen(x_pos, y_pos, width, height)
        # Не вся комната попадается на экран и, чтобы ускорить процесс отрисовки, находятся x и y,
        # которые нужно отрисовать
        for y in range(y1, y2):
            for x in range(x1, x2):
                for layer in layers:
                    if self.is_render_picture_walls in functions:
                        if self.is_render_picture_walls(x, y):  # отрисовка рисунков на стене
                            image = self.picture_walls[f'{x} {y}'][0].get_tile_image(
                                *self.picture_walls[f'{x} {y}'][-1], 0)
                            screen.blit(image, (x_pos + x * self.tile_size, y_pos + y * self.tile_size))
                            continue
                    if type(self) == Room and layer == 1 and y == 43 and type(self.walls_gates['bottom']) != Gate:
                        continue  # есть часть пола, которой нужно отрисовывать в определенные условия
                    image = map_surface.get_tile_image(x, y, layer)
                    if image:
                        screen.blit(image, (x_pos + x * self.tile_size, y_pos + y * self.tile_size))
                        if is_collide_with_speed in functions and layer == layers_collide:  # проверка коллизии объектов
                            x_speed, y_speed = is_collide_with_speed(player, image, x_pos + x * self.tile_size,
                                                                     y_pos + y * self.tile_size, x_speed, y_speed)
                        # если нужно перерисовать персонажей:
                        if self.redrawing and self.redrawing_player in functions:
                            self.redrawing = self.redrawing_player(player, image, x, y)
                        if self.redrawing_player in functions:
                            [self.redrawing_monsters.pop(i) for i in range(len(self.redrawing_monsters) - 1, -1, -1) if
                             not self.redrawing_player(self.redrawing_monsters[i], image, x, y)]

        return x_speed, y_speed

    def is_render_picture_walls(self, x, y):
        """Метод класса. Возвращает True, если есть рисунок стены с такими координатами иначе False"""
        return self.picture_walls.get(f'{x} {y}')

    def redrawing_player(self, player, image, x, y):
        """Метод класса. Возвращает True, если надо перерисовывать иначе False"""
        image_y = self.y + y * self.tile_size
        image_x = self.x + x * self.tile_size
        if 406 >= self.map.tiledgidmap[self.map.get_tile_gid(x, y, 3)] >= 404 and \
                is_collide(player, image, image_x, image_y, change_player=False):
            # именно здесь понадобился change_player
            return False
        if (image_y + self.tile_size >= player.rect.y + player.rect.height >= image_y and (
                player.rect.x + player.rect.width >= image_x >= player.rect.x or
                player.rect.x + player.rect.width >= image_x >= player.rect.x)):
            return False
        return True

    def is_collide_barrels_or_spike(self, player, x_speed, y_speed):
        """Метод класса. Проверяет коллизию между игроком и бочками комнаты и
        возвращает 0, если была коллизия иначе неизмененную скорость"""
        for i in self.barrel_group:
            if not any([x_speed, y_speed]):
                break
            x_speed, y_speed = i.is_collide(player, x_speed, y_speed)
        if pygame.sprite.spritecollideany(player, self.spike_group):
            [i.is_collide(player, is_stay_gates) for i in self.spike_group]
        return x_speed, y_speed

    def clear(self):
        """Метод класса. Удаляет спрайты объектов"""
        [i.kill() for i in self.torch_group]
        [i.kill() for i in self.spike_group]
        [i.die() for i in self.monster_group]
        [i.kill() for i in self.barrel_group]


class Room(RoomCorridor):
    """Класс Room. Создаёт комнату
        При инициализации принимает такие значение как:
        x - координата относительно квадрата 4*4
        y - координата относительно квадрата 4*4
        filename - имя файла комнаты"""

    def __init__(self, x, y, filename):
        super(Room, self).__init__(x, y, filename)
        self.possible_pos = [(x, y) for x in range(2, 40) for y in range(6, 43)]
        if self.filename_room not in ['room_with_chest', 'begin_room', 'end_room']:  # лишний раз не надо делать
            self._create_possible_positions_for_monster()
        self._add_flags()
        self._add_barrels_and_spike()
        [Cell(self.map.get_tile_image(x, y, 2), self.x + self.tile_size * x, self.y + self.tile_size * y)
         for x in range(self.width) for y in range(self.height)]
        if self.filename_room not in ['room_with_chest', 'begin_room', 'end_room']:
            self.cnt_wave = random.randrange(2, 4)  # Волн может быть от 3 до 5.
            # Одну мы уже подготовили, поэтому в переменной cnt_wave хранится на одну меньше волну
            self.delay = 60
        else:
            self.delay = 0
            self.cnt_wave = 0
        self.color = pygame.Color(255, 255, 255)  # его нужно менять потом

    def _create_possible_positions_for_monster(self):
        """Метод класса. Создание списка возможных координат создания монстров"""
        for x in range(self.width):
            for y in range(self.height):
                if self.map.get_tile_image(x, y, 2):
                    self._del_possible_pos_for_monster(x, y)

    def _add_flags(self):
        """Метод класса. В одном слое находит флажки и рисует определённые объекты"""
        if 'corridor' in self.filename_room:
            return
        # Зайдите в tiled editor map и посмотрите на комнаты в первом слое. Именно там отмечены флажки
        # Так как это происходит в самом начале, не вижу делать здесь оптимизацию
        for y in range(self.height):
            for x in range(self.width):
                if self.map.get_tile_image(x, y, 0):
                    if self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 1376:
                        sprites.Torch('torch_', self.x + self.tile_size * (x - 1),
                                      self.y + self.tile_size * (y - 1) - self.tile_size // 2, True)
                        self._del_possible_pos_for_monster(x, y)
                    elif self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 1441:
                        self.torch_group.add(sprites.Torch('torch_', self.x + self.tile_size * (x - 1),
                                                           self.y + self.tile_size * (y - 1) - self.tile_size // 2,
                                                           False))
                    elif self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 489:
                        sprites.Torch('candleA_0', self.x + self.tile_size * (x - 1),
                                      self.y + self.tile_size * (y - 1) - self.tile_size // 2, True)
                        self._del_possible_pos_for_monster(x, y)
                    elif self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 553:
                        self.torch_group.add(sprites.Torch('candleA_0', self.x + self.tile_size * (x - 1),
                                                           self.y + self.tile_size * (y - 1) - self.tile_size // 2,
                                                           False))
                    elif self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 615:
                        sprites.Torch('candleB_0', self.x + self.tile_size * (x - 1),
                                      self.y + self.tile_size * (y - 1), True)
                        self._del_possible_pos_for_monster(x, y)
                    elif self.map.tiledgidmap[self.map.get_tile_gid(x, y, 0)] == 550:
                        self.torch_group.add(sprites.Torch('candleB_0', self.x + self.tile_size * (x - 1),
                                                           self.y + self.tile_size * (y - 1), False))

    def _add_barrels_and_spike(self):
        """Метод класса. Создание бочек и шипов в комнате"""
        if self.filename_room not in ['room_with_chest', 'begin_room', 'end_room']:
            listok = os.listdir(path=f'{BAR_SPIKE_MAP_DIR}\\{self.filename_room}')
            listok.pop(listok.index('mainlevbuild.png'))
            listok.pop(listok.index('mainlevbuild.tsx'))
            listok.append('')
            filename = random.choice(listok)
            if filename == '':
                return
            map_surface = pytmx.load_pygame(f'{BAR_SPIKE_MAP_DIR}\\{self.filename_room}\\{filename}')
            for y in range(map_surface.height):
                for x in range(map_surface.width):
                    image = map_surface.get_tile_image(x, y, 0)
                    if image:
                        if map_surface.tiledgidmap[map_surface.get_tile_gid(x, y, 0)] % 2560 == 1261:
                            self.barrel_group.add(Barrel(self.x + (x - 1) * self.tile_size,
                                                         self.y + (y - 1) * self.tile_size))
                            self._del_possible_pos_for_monster(x, y)
                            self._del_possible_pos_for_monster(x - 1, y)
                            self._del_possible_pos_for_monster(x, y - 1)
                            self._del_possible_pos_for_monster(x - 1, y - 1)
                            self._del_possible_pos_for_monster(x - 1, y + 1)
                            self._del_possible_pos_for_monster(x, y + 1)
                        elif map_surface.tiledgidmap[map_surface.get_tile_gid(x, y, 0)] % 2560 == 1197:
                            self.spike_group.add(Spike(self.x + (x - 1) * self.tile_size,
                                                       self.y + (y - 1) * self.tile_size))

    def _del_possible_pos_for_monster(self, x, y):
        # это больше функция, чем метод класса, и здесь не требуется документация
        if (x, y) in self.possible_pos:
            self.possible_pos.pop(self.possible_pos.index((x, y)))
        if (x - 1, y) in self.possible_pos:
            self.possible_pos.pop(self.possible_pos.index((x - 1, y)))
        if (x - 2, y) in self.possible_pos:
            self.possible_pos.pop(self.possible_pos.index((x - 2, y)))

    def add_monsters(self, player, current_level):
        """Метод класса. Добавляет монстров в комнату"""
        if self.filename_room not in ['room_with_chest', 'begin_room', 'end_room']:
            cnt_monsters = random.randrange(4, 7)  # экспериментально
            for i in range(cnt_monsters):
                x, y = random.choice(self.possible_pos)
                monster = sprites.Ghoul(player=player, attack_range=10, running_speed=70, reward=10,
                                        center_pos=(self.x + self.tile_size * x, self.y + self.tile_size * y - 49),
                                        move_randomly=False, player_avoidance=False, current_level=current_level) \
                    if i % 2 == 0 else \
                    sprites.Zombie(player=player, move_randomly=True, attack_range=300,
                                   center_pos=(self.x + self.tile_size * x, self.y + self.tile_size * y - 28),
                                   player_avoidance=True, running_speed=70, current_level=current_level, reward=10)
                self.monster_group.add(monster)

    def render(self, screen, x_speed, y_speed, player):
        """Метод класса. Рисует пол и стены, через которых нельзя пройти + отрисовка других декораций"""
        x_speed, y_speed = super(Room, self).render(screen, x_speed, y_speed, player)
        self.set_is_stay_gates(player)  # меняем значение в переменной is_stay_gates перед отрисовкой ворот
        for key, wall in self.walls_gates.items():  # Отрисовка верхней стены или вороты
            # Верхняя стена не должна накладываться на персонажа, а должно быть наоборот. Поэтому
            if key == 'top':
                if type(wall) == Gate:
                    if is_stay_gates and self.filename_room not in ['room_with_chest', 'begin_room', 'end_room']:
                        wall.render(screen, is_stay_gates)
                        x_speed, y_speed = wall.is_collide(player, x_speed, y_speed, is_stay_gates)
                    else:
                        wall.cnt = 0
                    continue
                else:
                    x_speed, y_speed = self.blit_tiles(screen, wall, self.x, self.y, wall.width, wall.height, [0],
                                                       x_speed=x_speed, y_speed=y_speed,
                                                       player=player, layers_collide=0,
                                                       functions=[is_collide_with_speed,
                                                                  self.is_render_picture_walls])
                continue
        # Отрисовка других декораций:
        self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, range(4, len(self.map.layers)))
        x_speed, y_speed = self._render_and_collision_barrel_spike(screen, player, x_speed, y_speed)
        return x_speed, y_speed

    def _render_and_collision_barrel_spike(self, screen, player, x_speed, y_speed):
        """Метод класса. Отрисовка и проверка коллизии бочек и шипов"""
        self.barrel_group.draw(screen)
        self.spike_group.draw(screen)
        self._animation_spike()
        x_speed, y_speed = self.is_collide_barrels_or_spike(player, x_speed, y_speed)
        return x_speed, y_speed

    def render_passing_walls(self, screen, x_speed, y_speed, player):
        """Метод класса.
        Отрисовывает стены, через которые можно пройти, а также перерисовывает персонажей, если нужно"""
        [i.draw(screen) for i in self.monster_group]
        for key, wall in self.walls_gates.items():  # Отрисовка боковых ворот(левой и правой)
            if key == 'top' or key == 'bottom':
                continue
            if type(wall) == Gate:
                if is_stay_gates and self.filename_room not in ['room_with_chest', 'begin_room', 'end_room']:
                    wall.render(screen, is_stay_gates)
                    x_speed, y_speed = wall.is_collide(player, x_speed, y_speed, is_stay_gates)
                else:
                    wall.cnt = 0
                continue
        super(Room, self).render_passing_walls(screen, player)
        for key, wall in self.walls_gates.items():  # Отрисовка оставшиеся стены и ворота
            if key == 'top':  # Уже отрисовываны
                continue
            if type(wall) == Gate:
                if key == 'left' or key == 'right':  # Уже отрисовываны
                    continue
                if is_stay_gates and self.filename_room not in ['room_with_chest', 'begin_room', 'end_room']:
                    wall.render(screen, is_stay_gates)
                    x_speed, y_speed = wall.is_collide(player, x_speed, y_speed, is_stay_gates)
                else:
                    wall.cnt = 0
                continue
            is_bottom = ((self.height - 3) * self.tile_size) if wall.filename.find(
                'bottom') != -1 else 0  # если нижняя стена
            # если правая стена:
            is_right = ((self.width - 2) * self.tile_size) if wall.filename.find('right') != -1 else 0
            x_speed, y_speed = self.blit_tiles(screen, wall, is_right + self.x, is_bottom + self.y, wall.width,
                                               wall.height, range(len(wall.layers)), functions=[is_collide_with_speed],
                                               x_speed=x_speed, y_speed=y_speed, player=player, layers_collide=0)

        return x_speed, y_speed

    def set_walls(self, left, right, top, bottom):
        """Метод класса. Создает стены и ворота"""
        # Либо стена, либо коридор, где на концах расположены ворота
        self.walls_gates = {
            'left': pytmx.load_pygame(f'{TILED_MAP_DIR}\\left_wall.tmx') if left else
            Gate(self.x + self.tile_size,
                 self.y + self.tile_size * self.height // 2 - 7 * self.tile_size, 'vertical'),
            'right': pytmx.load_pygame(f'{TILED_MAP_DIR}\\right_wall.tmx') if right else
            Gate(self.x + self.tile_size * self.width - self.tile_size * 2,
                 self.y + self.tile_size * self.height // 2 - 7 * self.tile_size, 'vertical'),
            'top': pytmx.load_pygame(f'{TILED_MAP_DIR}\\top_wall.tmx') if top else
            Gate(self.x + self.tile_size * self.width // 2 - 4 * self.tile_size,
                 self.y + self.tile_size, 'horizontal', top_or_bottom='top'),
            'bottom': pytmx.load_pygame(f'{TILED_MAP_DIR}\\bottom_wall.tmx') if bottom else
            Gate(self.x + self.tile_size * self.width // 2 - 4 * self.tile_size,
                 self.y + self.tile_size * self.height - self.tile_size * 3, 'horizontal'),
        }
        for key, wall in self.walls_gates.items():
            if type(wall) != Gate:
                is_bottom = ((self.height - 3) * self.tile_size) if key == 'bottom' else 0  # если нижняя стена
                # если правая стена:
                is_right = ((self.width - 2) * self.tile_size) if key == 'right' else 0
                [Cell(wall.get_tile_image(x, y, 0), self.x + self.tile_size * x + is_right,
                      self.y + self.tile_size * y + is_bottom)
                 for x in range(wall.width) for y in range(wall.height)]  # нужно для коллизии с пулей

        self.set_picture_walls(0 if type(self.walls_gates['top']) == Gate else 1)

    def set_picture_walls(self, top_wall):
        """Метод класса. Создает рисунки на стене"""
        x_pos = 2
        for _ in range(8):
            pic_wall = pytmx.load_pygame(random.choice(PICTURE_WAllS))
            if not top_wall and x_pos == 20:
                x_pos += 6
                continue
            i = 0
            for x in range(x_pos, x_pos + 4):
                j = 0
                for y in range(1, 4):
                    self.picture_walls[f'{x} {y}'] = [pic_wall, (i, j)]
                    j += 1
                i += 1
            x_pos += 6

    def move(self, x, y):
        """Метод класса. Движение комнат с его объектами"""
        # Особенность движения объектов: двигается не персонаж(он все время стоит на месте относительно экрана),
        # а комнаты и другие объекты
        super(Room, self).move(x, y)
        [wall.move(x, y) for key, wall in self.walls_gates.items() if type(wall) == Gate]

    def self_move_of_monster(self):
        """Метод класса. Проверка коллизии монстров и их движение"""
        if is_stay_gates and len(self.monster_group.sprites()):
            self.monster_group.update()
            monsters = [i for i in self.monster_group.sprites()]
            # не все монстры дойдут до конца цикла, так как некоторым необязательно проверять коллизию,
            # если у них скорость равно 0
            for wall in self.walls_gates.items():  # коллизия между монстрами и стенами по бокам или воротами
                key, wall = wall
                # если нижняя стена:
                is_bottom = ((self.height - 3) * self.tile_size) if key == 'bottom' else 0  # если нижняя стена
                # если правая стена:
                is_right = ((self.width - 2) * self.tile_size) if key == 'right' else 0
                if type(wall) == Gate:  # если wall - ворота, а не стена
                    for i in range(len(monsters) - 1, -1, -1):
                        monster = monsters[i]
                        monster.move_x, monster.move_y = wall.is_collide(monster, monster.move_x, monster.move_y,
                                                                         is_stay_gates)
                        if 0 == monster.move_x and monster.move_y == 0:
                            # если его скорость равна нулю, то дальше проверять коллизию его нет смысла
                            del monsters[i]
                    if not monsters:  # если у всех монстров скорость равна нулю, то завершается метод класса
                        [i.self_move() for i in self.monster_group]
                        return
                    continue
                for i in range(len(monsters) - 1, -1, -1):
                    monster = monsters[i]
                    monster.collide_with_wall(self.x + is_right, is_bottom + self.y, wall, 0, self.tile_size)
                    if monster.move_x == 0 and monster.move_y == 0:
                        # если его скорость равна нулю, то дальше проверять коллизию его нет смысла
                        del monsters[i]
                if not monsters:  # если у всех монстров скорость равна нулю, то завершается метод класса
                    [i.self_move() for i in self.monster_group]
                    return
            for i in range(len(monsters) - 1, -1, -1):  # коллизия между монстрами и непроходимой стеной
                monster = monsters[i]
                monster.collide_with_wall(self.x, self.y, self.map, 2, self.tile_size)
                if monster.move_x == 0 and monster.move_y == 0:
                    # если его скорость равна нулю, то дальше проверять коллизию его нет смысла
                    del monsters[i]
            if not monsters:  # если у всех монстров скорость равна нулю, то завершается метод класса
                [i.self_move() for i in self.monster_group]
                return
            for i in range(len(monsters) - 1, -1, -1):  # коллизия между монстрами и бочками
                monster = monsters[i]
                for barrel in self.barrel_group:
                    monster.move_x, monster.move_y = barrel.is_collide(monster, monster.move_x,
                                                                       monster.move_y)
                    if 0 == monster.move_x and monster.move_y == 0:
                        # если его скорость равна нулю, то дальше проверять коллизию его нет смысла
                        del monsters[i]
                        break
            if not monsters:  # если у всех монстров скорость равна нулю, то завершается метод класса
                [i.self_move() for i in self.monster_group]
                return
            for i in range(len(monsters) - 1, -1, -1):  # коллизия между монстрами и свечами
                monster = monsters[i]
                for torch in sprites.torch_group:
                    monster.move_x, monster.move_y = torch.is_collide(monster, monster.move_x,
                                                                      monster.move_y)
                    if 0 == monster.move_x and monster.move_y == 0:
                        # если его скорость равна нулю, то дальше проверять коллизию его нет смысла
                        del monsters[i]
                        break
            [i.self_move() for i in self.monster_group]

    def _animation_spike(self):
        # это больше функция, чем метод класса, и здесь не требуется документация
        [i.increment_cnt() for i in self.spike_group]

    def enter_next_level(self, player):
        """Метод класса. Возвращает True, если можно перейти на следующий уровень"""
        if self.filename_room == 'end_room':  # на всякий случай защита от других комнат
            for x in range(17, 27):  # Отмерено при помощи tiled editor map
                for y in range(20, 23):
                    cell = pygame.sprite.Sprite()
                    cell.rect = pygame.Rect(self.x + x * self.tile_size, self.y + y * self.tile_size,
                                            self.tile_size, self.tile_size)
                    if pygame.sprite.collide_rect(player, cell):
                        return True
        return False

    def new_wave(self, screen, player, current_level):
        """Метод класса. Создание новой волны монстров"""
        if self.monster_group or self.cnt_wave == 0 or self.filename_room in \
                ['room_with_chest', 'begin_room', 'end_room']:
            if self.filename_room not in ['room_with_chest', 'begin_room', 'end_room'] and self.cnt_wave == 0 and \
                    not self.monster_group:
                hsv = self.color.hsva
                if hsv[2] >= 10:
                    self.color.hsva = (hsv[0], hsv[1], hsv[2] - 1, hsv[3])
                    font = pygame.font.Font('ui/MinimalPixel v2.ttf', 30).render('The room is clear', True, self.color)
                    screen.blit(font, (others.WIDTH // 2 - font.get_width() // 2, 150))
            return
        if not self.monster_group and self.delay:
            self.delay -= 1
        elif not self.monster_group and not self.delay:
            self.delay = 60
            self.add_monsters(player, current_level)
            self.cnt_wave -= 1

    def set_is_stay_gates(self, player):
        """Метод класса. Меняет значение переменной is_stay_gates"""
        global is_stay_gates
        if self.x + 2 * self.tile_size < player.rect.x < player.rect.x + player.rect.width < \
                self.x + self.tile_size * 42 and \
                self.y + 43 * self.tile_size > player.rect.y + player.rect.height > player.rect.y + player.rect.height \
                // 1.5 > self.y + 5 * self.tile_size and (
                self.monster_group or self.cnt_wave):
            is_stay_gates = True
        else:
            is_stay_gates = False


class Corridor(RoomCorridor):
    """Класс Corridor. Создаёт коридор
        При инициализации принимает такие значение как:
        x - координата относительно квадрата 4*4
        y - координата относительно квадрата 4*4
        orientation - вертикальный коридор(vertical) или горизонтальный(horizontal)"""

    def __init__(self, x, y, orientation):
        super(Corridor, self).__init__(x, y, f'{orientation}_corridor')
        if orientation == 'vertical':
            self.y += 672
            self.x += 288
        else:
            self.x += 672
            self.y += 336 - self.tile_size * 13 // 2 - 8
        [Cell(self.map.get_tile_image(x, y, 2), self.x + self.tile_size * x, self.y + self.tile_size * y)
         for x in range(self.width) for y in range(self.height)]
        [Cell(self.map.get_tile_image(x, y, 4), self.x + self.tile_size * x, self.y + self.tile_size * y)
         for x in range(self.width) for y in range(self.height)]

    def render(self, screen, x_speed, y_speed, player):
        """Метод класса. Рисует пол и стены, через которых нельзя пройти + отрисовка других декораций"""
        x_speed, y_speed = super(Corridor, self).render(screen, x_speed, y_speed, player)
        if not is_stay_gates:
            self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height,
                            range(4, len(self.map.layers)))
        return x_speed, y_speed

    def render_passing_walls(self, screen, player):
        """Метод класса. Отрисовка стен, через которые можно пройти"""
        self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, [3])
