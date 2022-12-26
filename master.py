import pygame
import pytmx
import random


# комната 704*704
# протяженность коридора 512 - 32

class Room:
    def __init__(self, x, y):
        self.map = pytmx.load_pygame(f'map\\ready_map\\map{random.randrange(1, 4)}.tmx')
        self.x = x * (704 + 512)
        self.y = y * (704 + 512)
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                for layer in range(len(self.map.layers)):
                    image = self.map.get_tile_image(x, y, layer)
                    if image:
                        screen.blit(image, (self.x + x * self.tile_size, self.y + y * self.tile_size))

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


class Corridor:
    def __init__(self, x, y, orientation):
        self.map = pytmx.load_pygame(f'map\\ready_map\\{orientation}_corridor.tmx')
        # 672 +
        self.x = x * (704 + 512)
        self.y = y * (704 + 512)
        if orientation == 'vertical':
            self.y += 672
        else:
            self.x += 672
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                for layer in range(len(self.map.layers)):
                    image = self.map.get_tile_image(x, y, layer)
                    if image:
                        screen.blit(image, (self.x + x * self.tile_size, self.y + y * self.tile_size))

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


class Labyrinth:
    def __init__(self):
        self.count_room = random.randrange(1, 4)  # кол-во комнат в уровне,
        # без учета первой комнаты, комнаты с врагами(их 2) и последней комнаты
        self.map_list = list([0] * 4 for _ in range(4))

        self.rooms = []
        self.corridors = []

        x, y = random.randrange(4), random.randrange(4)
        room = Room(x, y)
        self.map_list[y][x] = room
        self.rooms.append(room)

        for i in range(3):  # создание основной цепи комнат, то есть те комнаты, которые должны пройти
            while True:
                kx, ky = random.choice([(0, -1), (0, 1), (1, 0), (-1, 0)])
                if 4 > x + kx >= 0 and 4 > y + ky >= 0 and not self.map_list[y + ky][x + kx]:
                    if kx:
                        self.corridors.append(Corridor(min(x, x + kx), y, 'horizontal'))
                    else:
                        self.corridors.append(Corridor(x, min(y, y + kx), 'vertical'))
                    x, y = x + kx, y + ky
                    room = Room(x, y)
                    self.map_list[y][x] = room
                    self.rooms.append(room)

                    break
        print(*self.map_list, sep='\n')

    def update(self, screen):
        for room in self.rooms:
            room.move()
            if self.collide_rect(0, 0, width, height,
                                 room.x, room.y, room.x + room.width * room.tile_size,
                                 room.y + room.height * room.tile_size):
                room.render(screen)

        for corridor in self.corridors:
            corridor.move()
            if self.collide_rect(0, 0, width, height,
                                 corridor.x, corridor.y, corridor.x + corridor.width * corridor.tile_size,
                                 corridor.y + corridor.height * corridor.tile_size):
                corridor.render(screen)

    def collide_rect(self, ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
        """Пересечение прямоугольников"""
        # Создан для оптимизации отрисовки, то есть отрисовываются только те комнаты, которые находятся в экране,
        # а не за ним
        s1 = (ax1 >= bx1 and ax1 <= bx2) or (ax2 >= bx1 and ax2 <= bx2)
        s2 = (ay1 >= by1 and ay1 <= by2) or (ay2 >= by1 and ay2 <= by2)
        s3 = (bx1 >= ax1 and bx1 <= ax2) or (bx2 >= ax1 and bx2 <= ax2)
        s4 = (by1 >= ay1 and by1 <= ay2) or (by2 >= ay1 and by2 <= ay2)
        return True if ((s1 and s2) or (s3 and s4)) or ((s1 and s4) or (s3 and s2)) else False


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Game')
    size = width, height = 600, 600  # скорее всего изменится
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    FPS = 60
    running = True
    lab = Labyrinth()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        lab.update(screen)
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()
