import pygame
import pytmx
from others import WIDTH, HEIGHT, TILED_MAP_DIR


# комната 704*704
# протяженность коридора 512 - 32

class RoomCorridor:

    def __init__(self, x, y, filename):
        self.map = pytmx.load_pygame(f'{TILED_MAP_DIR}\\{filename}.tmx')
        self.x = x * (704 + 512)
        self.y = y * (704 + 512)
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth

    def render(self, screen):
        x1, y1, x2, y2 = self.rect_in_screen(self.x, self.y, self.width, self.height)
        for y in range(y1, y2):
            for x in range(x1, x2):
                for layer in range(len(self.map.layers)):
                    image = self.map.get_tile_image(x, y, layer)
                    if image:
                        screen.blit(image, (self.x + x * self.tile_size, self.y + y * self.tile_size))

    def rect_in_screen(self, x, y, width_dec, height_dec):
        """Возвращает начальные и конечные координаты ячеек комнаты, которые попадают на экран"""
        # Без этой оптимизации процесс отрисовки был бы ОЧЕНЬ долгим и просаживался бы FPS
        x1 = max(0, x)
        x2 = min(WIDTH, width_dec * self.tile_size + x)
        x1 = 0 if x1 == x else (-x // self.tile_size)
        x2 = width_dec if x2 == width_dec * self.tile_size + x \
            else width_dec - (width_dec * self.tile_size + x - WIDTH) // self.tile_size
        y1 = max(0, y)
        y2 = min(HEIGHT, height_dec * self.tile_size + y)
        y1 = 0 if y1 == y else (-y // self.tile_size)
        y2 = height_dec if y2 == height_dec * self.tile_size + y \
            else height_dec - (height_dec * self.tile_size + y - HEIGHT) // self.tile_size
        return x1, y1, x2, y2

    def move(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_w] or key[pygame.K_UP]:
            self.y += 10
        if key[pygame.K_s] or key[pygame.K_DOWN]:
            self.y -= 10
        if key[pygame.K_a] or key[pygame.K_LEFT]:
            self.x += 10
        if key[pygame.K_d] or key[pygame.K_RIGHT]:
            self.x -= 10


class Room(RoomCorridor):
    def __init__(self, x, y, filename):
        super(Room, self).__init__(x, y, filename)
        self.walls = []

    def render(self, screen):
        super(Room, self).render(screen)
        for wall in self.walls:
            is_bottom = ((self.height - 3) * self.tile_size) if wall.filename.find(
                'bottom') != -1 else 0  # если нижняя стена
            # если правая стена:
            is_right = ((self.width - 2) * self.tile_size) if wall.filename.find('right') != -1 else 0
            x1, y1, x2, y2 = self.rect_in_screen(is_right + self.x, is_bottom + self.y, wall.width, wall.height)
            for y in range(y1, y2):
                for x in range(x1, x2):
                    image = wall.get_tile_image(x, y, 0)
                    if image:
                        screen.blit(image,
                                    (self.x + x * self.tile_size + is_right, self.y + y * self.tile_size + is_bottom))

    def set_walls(self, left, right, top, bottom):
        self.walls = []
        walls = ['left' if left else 0, 'right' if right else 0, 'top' if top else 0, 'bottom' if bottom else 0]
        for i in walls:
            if i:
                self.walls.append(pytmx.load_pygame(f'{TILED_MAP_DIR}\\{i}_wall.tmx'))


class Corridor(RoomCorridor):
    def __init__(self, x, y, orientation):
        super(Corridor, self).__init__(x, y, f'{orientation}_corridor')
        if orientation == 'vertical':
            self.y += 672
        else:
            self.x += 672

    def move(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_w] or key[pygame.K_UP]:
            self.y += 10
        if key[pygame.K_s] or key[pygame.K_DOWN]:
            self.y -= 10
        if key[pygame.K_a] or key[pygame.K_LEFT]:
            self.x += 10
        if key[pygame.K_d] or key[pygame.K_RIGHT]:
            self.x -= 10
