import random
import pygame
import pytmx
from others import TILED_MAP_DIR, PICTURE_WAllS
import others

# комната 704*704
# протяженность коридора 512 - 32
is_stay_gates = False  # Стоят ли ворота. Она понадобилась в одном деле


class RoomCorridor:

    def __init__(self, x, y, filename):
        self.map = pytmx.load_pygame(f'{TILED_MAP_DIR}\\{filename}.tmx')
        self.x = x * (704 + 512)
        self.y = y * (704 + 512)
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.picture_walls = dict()
        self.top_wall = False  # есть наверху полная стена или там коридор
        self.redrawing = True
        self.walls_gates = dict()

    def render(self, screen, x_speed, y_speed, player):
        x_speed, y_speed = self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, range(2),
                                           functions=[self.is_render_picture_walls, self.is_collising],
                                           player=player, x_speed=x_speed,
                                           y_speed=y_speed)
        return x_speed, y_speed

    def render_passing_walls(self, screen, player):
        self.redrawing = True
        self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, [2],
                        functions=[self.redrawing_player],
                        player=player)
        if self.redrawing:
            player.draw()

    def rect_in_screen(self, x, y, width_dec, height_dec):
        """Возвращает начальные и конечные координаты ячеек комнаты, которые попадают на экран"""
        # Без этой оптимизации процесс отрисовки был бы ОЧЕНЬ долгим и просаживался бы FPS
        x1 = max(0, x)
        x2 = min(others.WIDTH, width_dec * self.tile_size + x)
        x1 = 0 if x1 == x else (-x // self.tile_size)
        x2 = width_dec if x2 == width_dec * self.tile_size + x \
            else width_dec - (width_dec * self.tile_size + x - others.WIDTH) // self.tile_size
        y1 = max(0, y)
        y2 = min(others.HEIGHT, height_dec * self.tile_size + y)
        y1 = 0 if y1 == y else (-y // self.tile_size)
        y2 = height_dec if y2 == height_dec * self.tile_size + y \
            else height_dec - (height_dec * self.tile_size + y - others.HEIGHT) // self.tile_size
        return x1, y1, x2, y2

    def move(self, x, y):
        self.x -= x
        self.y -= y

    def is_collising(self, player, image, x, y, x_speed, y_speed):
        # Можно сказать, создаем спрайт ячейки для проверки коллизии
        if any([x_speed, y_speed]):
            cell = pygame.sprite.Sprite()
            cell.image = image
            cell.rect = image.get_rect()
            cell.rect.y = y
            height = player.rect.height  # сохранить точность роста персонажа
            cell.rect.x = x - x_speed
            player.rect.y += player.rect.height // 1.01  # Мы смотрим коллизию по ногам, а не по телу
            player.rect.height -= player.rect.height // 1.01
            if pygame.sprite.collide_rect(cell, player):
                cell.rect.x = cell.rect.x + x_speed
                x_speed = 0
            else:
                cell.rect.x = cell.rect.x + x_speed
            cell.rect.y = cell.rect.y - y_speed
            if pygame.sprite.collide_rect(cell, player):
                y_speed = 0
            cell.kill()  # утечка памяти
            player.rect.height = height  # возвращаем как было
            player.rect.y -= player.rect.height // 1.01

        return x_speed, y_speed

    def blit_tiles(self, screen, room, x_pos, y_pos, w, h, layers, functions=[], is_top_wall=False,
                   x_speed=None, y_speed=None, player=None, layers_collide=1):
        x1, y1, x2, y2 = self.rect_in_screen(x_pos, y_pos, w, h)
        for y in range(y1, y2):
            for x in range(x1, x2):
                for layer in layers:
                    if self.is_render_picture_walls in functions:
                        if (is_top_wall or layer == 1) and self.is_render_picture_walls(x, y):
                            image = self.picture_walls[f'{x} {y}'][0].get_tile_image(
                                *self.picture_walls[f'{x} {y}'][-1], 0)
                            screen.blit(image, (x_pos + x * self.tile_size, y_pos + y * self.tile_size))
                            continue
                    if layer == 0 and y == 43 and type(self.walls_gates['bottom']) != Gate:
                        continue
                    image = room.get_tile_image(x, y, layer)
                    if image:
                        screen.blit(image, (x_pos + x * self.tile_size, y_pos + y * self.tile_size))
                        if self.is_collising in functions and layer == layers_collide:
                            x_speed, y_speed = self.is_collising(player, image, x_pos + x * self.tile_size,
                                                                 y_pos + y * self.tile_size, x_speed, y_speed)
                        if self.redrawing_player in functions:
                            self.redrawing_player(player, x, y)
        if x_speed is not None:
            return x_speed, y_speed

    def is_render_picture_walls(self, x, y):
        return self.picture_walls.get(f'{x} {y}')

    def redrawing_player(self, player, x, y):
        image_y = self.y + y * self.tile_size
        image_x = self.x + x * self.tile_size
        if 406 >= self.map.tiledgidmap[self.map.get_tile_gid(x, y, 2)] >= 404 or \
                (image_y + self.tile_size >= player.rect.y + player.rect.height >= image_y and (
                        player.rect.x + player.rect.width >= image_x >= player.rect.x or
                        player.rect.x + player.rect.width >= image_x >= player.rect.x)):
            # сложно объяснить зачем условие: делает, можно сказать, 3D объекты-декорации
            self.redrawing = False


class Room(RoomCorridor):
    def __init__(self, x, y, filename):
        super(Room, self).__init__(x, y, filename)

    def render(self, screen, x_speed, y_speed, player):
        x_speed, y_speed = super(Room, self).render(screen, x_speed, y_speed, player)
        for key, wall in self.walls.items():
            # Верхняя стена не должна накладываться на персонажа, а должно быть наоборот. Поэтому
            if key == 'top':
                if type(wall) == Gate:
                    if is_stay_gates:
                        wall.render(screen)
                else:
                    x_speed, y_speed = self.blit_tiles(screen, wall, self.x, self.y, wall.width,
                                                       wall.height, [0], x_speed=x_speed, y_speed=y_speed,
                                                       player=player,
                                                       functions=[self.is_collising, self.is_render_picture_walls],
                                                       layers_collide=0, is_top_wall=True)
                continue
        self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, range(3, len(self.map.layers)))
        return x_speed, y_speed

    def render_passing_walls(self, screen, x_speed, y_speed, player):
        super(Room, self).render_passing_walls(screen, player)
        for key, wall in self.walls.items():
            if key == 'top':
                continue
            if type(wall) == Gate:
                if is_stay_gates:
                    wall.render(screen)
                continue
            is_bottom = ((self.height - 3) * self.tile_size) if wall.filename.find(
                'bottom') != -1 else 0  # если нижняя стена
            # если правая стена:
            is_right = ((self.width - 2) * self.tile_size) if wall.filename.find('right') != -1 else 0
            x_speed, y_speed = self.blit_tiles(screen, wall, is_right + self.x, is_bottom + self.y, wall.width,
                                               wall.height, range(len(wall.layers)), functions=[self.is_collising],
                                               x_speed=x_speed, y_speed=y_speed, player=player, layers_collide=0)
        return x_speed, y_speed

    def set_walls(self, left, right, top, bottom):
        # Либо стена, либо коридор, где на концах расположены ворота
        self.walls = {
            'left': pytmx.load_pygame(f'{TILED_MAP_DIR}\\left_wall.tmx') if left else
            Gate(self.x + self.tile_size,
                 self.y + self.tile_size * self.height // 2 - 7 * self.tile_size, 'vertical'),
            'right': pytmx.load_pygame(f'{TILED_MAP_DIR}\\right_wall.tmx') if right else
            Gate(self.x + self.tile_size * self.width - self.tile_size * 2,
                 self.y + self.tile_size * self.height // 2 - 7 * self.tile_size, 'vertical'),
            'top': pytmx.load_pygame(f'{TILED_MAP_DIR}\\top_wall.tmx') if top else
            Gate(self.x + self.tile_size * self.width // 2 - 3 * self.tile_size,
                 self.y + self.tile_size, 'horizontal', top_or_bottom='top'),
            'bottom': pytmx.load_pygame(f'{TILED_MAP_DIR}\\bottom_wall.tmx') if bottom else
            Gate(self.x + self.tile_size * self.width // 2 - 3 * self.tile_size,
                 self.y + self.tile_size * self.height - self.tile_size * 3, 'horizontal'),
        }
        self.top_wall = 0 if type(self.walls['top']) == Gate else 1
        self.set_picture_walls()

    def set_picture_walls(self):
        x_pos = 2
        for _ in range(8):
            pic_wall = pytmx.load_pygame(random.choice(PICTURE_WAllS))
            if not self.top_wall and x_pos == 20:
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
        super(Room, self).move(x, y)
        for key, wall in self.walls.items():
            if type(wall) == Gate:
                wall.move(x, y)


class Corridor(RoomCorridor):
    def __init__(self, x, y, orientation):
        super(Corridor, self).__init__(x, y, f'{orientation}_corridor')
        if orientation == 'vertical':
            self.y += 672
            self.x += 288
        else:
            self.x += 672
            self.y += 336 - self.tile_size * 13 // 2 - 8

    def render(self, screen, x_speed, y_speed, player):
        global is_stay_gates
        is_stay_gates = False if \
            self.x <= others.WIDTH // 2 <= self.x + self.width * self.tile_size and \
            self.y <= others.HEIGHT // 2 <= self.y + self.height * self.tile_size else True
        x_speed, y_speed = super(Corridor, self).render(screen, x_speed, y_speed, player)
        if not is_stay_gates:
            self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, range(3, len(self.map.layers)))
        return x_speed, y_speed

    def render_passing_walls(self, screen, player):
        self.blit_tiles(screen, self.map, self.x, self.y, self.width, self.height, [2])


class Gate:
    def __init__(self, x, y, orientation, top_or_bottom=False):
        self.map = pytmx.load_pygame(TILED_MAP_DIR + f'\\{orientation}_gate.tmx')
        self.speed = 5
        self.x = x
        self.y = y
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        # Чтобы не делать два файла ворот разных размеров (6*3 и 6*4), решил сделать так:
        self.top = True if top_or_bottom == 'top' else False

    def move(self, x, y):
        # self.y += self.speed
        self.x -= x
        self.y -= y

    def render(self, screen):
        for layer in range(len(self.map.layers)):
            for x in range(self.width):
                for y in range(self.height):
                    image = self.map.get_tile_image(x, y, layer)
                    if image:
                        if self.top and y == 2:
                            y += 1
                        screen.blit(image, (self.x + self.tile_size * x,
                                            self.y + self.tile_size * y))
                        if self.top and y == 1:
                            screen.blit(image, (self.x + self.tile_size * x,
                                                self.y + self.tile_size * (1 + y)))
