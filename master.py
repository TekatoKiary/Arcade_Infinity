import pygame
import random
from others import WIDTH, HEIGHT, SIZE, collide_rect, FPS
from room import Room, Corridor


class Labyrinth:
    def __init__(self):

        self.map_list = list([0] * 4 for _ in range(4))

        self.rooms = []
        self.corridors = []
        self.create_rooms()
        print(*self.map_list, sep='\n')

    def create_rooms(self):
        count_room = random.randrange(1, 4)
        # кол-во доп комнат в уровне,
        # то есть без учета первой комнаты, комнаты с врагами(их 2) и последней комнаты
        chess_room = random.randrange(count_room)
        coords_all_room = []  # список координат комнат
        coords_hor_cor = []  # список координат горизонтальных коридоров
        coords_ver_cor = []  # список координат вертикальных коридоров
        x, y = random.randrange(4), random.randrange(4)
        room = Room(x, y, f'begin_room')
        coords_all_room.append((x, y))
        self.map_list[y][x] = room
        self.rooms.append(room)
        for i in range(3):  # создание основной цепи комнат, то есть те комнаты, которые должны пройти
            d = [(0, -1), (0, 1), (1, 0), (-1, 0)]
            while 1:
                kx, ky = random.choice(d)
                if 4 > x + kx >= 0 and 4 > y + ky >= 0 and not self.map_list[y + ky][x + kx]:
                    if kx:
                        self.corridors.append(Corridor(min(x, x + kx), y, 'horizontal'))
                        coords_hor_cor.append((min(x, x + kx), y))
                    else:
                        self.corridors.append(Corridor(x, min(y, y + ky), 'vertical'))
                        coords_ver_cor.append((x, min(y, y + ky)))
                    x, y = x + kx, y + ky
                    room = Room(x, y, f'map{random.randrange(1, 4)}') \
                        if i < 2 else Room(x, y, f'end_room')
                    self.map_list[y][x] = room
                    self.rooms.append(room)
                    coords_all_room.append((x, y))
                    break
                else:
                    del d[d.index((kx, ky))]
        while count_room != -1:  # создание доп комнат
            x, y = random.randrange(4), random.randrange(4)
            if not self.map_list[y][x]:
                for kx, ky in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
                    if 4 > x + kx >= 0 and 4 > y + ky >= 0 and self.map_list[y + ky][x + kx] \
                            and self.rooms[0] != self.map_list[y + ky][x + kx] and \
                            self.rooms[3] != self.map_list[y + ky][x + kx]:
                        room = Room(x, y,
                                    f'map{random.randrange(1, 4)}' if chess_room == count_room else 'room_with_chess')
                        self.map_list[y][x] = room
                        self.rooms.append(room)
                        coords_all_room.append((x, y))
                        if kx:
                            self.corridors.append(Corridor(min(x, x + kx), y, 'horizontal'))
                            coords_hor_cor.append((min(x, x + kx), y))
                        else:
                            self.corridors.append(Corridor(x, min(y, y + ky), 'vertical'))
                            coords_ver_cor.append((x, min(y, y + ky)))
                        break
                if self.map_list[y][x]:
                    count_room -= 1
        for x, y in coords_all_room:  # вместо того чтобы просто пройтись по self.map_list лучше это
            walls = []
            for kx, ky in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                # Последние два условия проверяет на наличие коридоров между ними
                if 4 > x + kx >= 0 and 4 > y + ky >= 0 and self.map_list[y + ky][x + kx] and \
                        (kx == 0 or (min(x, kx + x), y) in coords_hor_cor) and \
                        (ky == 0 or (x, min(y, ky + y)) in coords_ver_cor):
                    walls.append(0)
                else:
                    walls.append(1)
            self.map_list[y][x].set_walls(*walls)

    def update(self, screen):
        x, y = move()
        for room in self.rooms:
            if collide_rect(0, 0, 1360, 780,
                            room.x, room.y, room.x + room.width * room.tile_size,
                            room.y + room.height * room.tile_size):
                x, y = room.render(screen, x, y, player)
        for corridor in self.corridors:
            if collide_rect(0, 0, WIDTH, HEIGHT,
                            corridor.x, corridor.y, corridor.x + corridor.width * corridor.tile_size,
                            corridor.y + corridor.height * corridor.tile_size):
                x, y = corridor.render(screen, x, y, player)
        player.draw()

        for room in self.rooms:
            if collide_rect(0, 0, 1360, 780,
                            room.x, room.y, room.x + room.width * room.tile_size,
                            room.y + room.height * room.tile_size):
                room.render_passing_walls(screen)

        for corridor in self.corridors:
            if collide_rect(0, 0, WIDTH, HEIGHT,
                            corridor.x, corridor.y, corridor.x + corridor.width * corridor.tile_size,
                            corridor.y + corridor.height * corridor.tile_size):
                corridor.render_passing_walls(screen)
        player.move()
        if x or y:
            [i.move(x, y) for i in self.rooms]
            [i.move(x, y) for i in self.corridors]


class Player(pygame.sprite.Sprite):
    # Временно
    def __init__(self, ):
        super(Player, self).__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA, 32)
        self.image.get_rect()

        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2
        self.mask = pygame.mask.from_surface(self.image)
        pygame.draw.rect(screen, (255, 191, 0), (self.x, self.y, *self.image.get_size()))

    def draw(self):
        pygame.draw.rect(screen, (255, 191, 0), (self.x, self.y, *self.image.get_size()))

    def move(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2


def move():
    key = pygame.key.get_pressed()
    x, y = 0, 0
    if key[pygame.K_w] or key[pygame.K_UP]:
        y = -10
    if key[pygame.K_s] or key[pygame.K_DOWN]:
        y = 10
    if key[pygame.K_a] or key[pygame.K_LEFT]:
        x = -10
    if key[pygame.K_d] or key[pygame.K_RIGHT]:
        x = 10
    return x, y


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Game')
    screen = pygame.display.set_mode(SIZE)
    # pygame.FULLSCREEN | pygame.DOUBLEBUF
    clock = pygame.time.Clock()

    running = 1
    lab = Labyrinth()
    player = Player()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        lab.update(screen)
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()
