import pygame
import pytmx
import random


# комната 512*512
# протяженность коридора 168

class Room:
    def __init__(self, x, y):
        self.map = pytmx.load_pygame(f'map\\ready_map\\map{random.randrange(1, 4)}.tmx')
        self.x = x * (512 + 168)
        self.y = y * (512 + 168)
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

        x, y = random.randrange(4), random.randrange(4)
        self.map_list[y][x] = Room(x, y)
        for i in range(3):  # создание основной цепи комнат, то есть те комнаты, которые должны пройти
            while True:
                kx, ky = random.choice([(0, -1), (0, 1), (1, 0), (-1, 0)])
                if 4 > x + kx >= 0 and 4 > y + ky >= 0 and not self.map_list[y + ky][x + kx]:
                    x, y = x + kx, y + ky
                    self.map_list[y][x] = Room(x, y)
                    break
        print(*self.map_list, sep='\n')

    def update(self, screen):
        for row in self.map_list:
            for room in row:
                if room:
                    room.move()
                    room.render(screen)


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
