import pygame
import random
import others
from others import collide_rect, FPS, barrels_coords
from room import Room, Corridor
from sprites import Player, Barrel


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
        chest_room = random.randrange(count_room)
        coords_all_room = []  # список координат комнат
        coords_hor_cor = []  # список координат горизонтальных коридоров
        coords_ver_cor = []  # список координат вертикальных коридоров

        x, y = random.randrange(4), random.randrange(4)
        room = Room(x, y, f'begin_room')
        coords_all_room.append((x, y))

        x_move = room.x + (-others.WIDTH + room.tile_size * room.width) // 2
        y_move = room.y + (-others.HEIGHT + room.tile_size * room.height) // 2

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
                    if barrels_coords.get(room.filename_room):
                        random_coords = random.choice(barrels_coords[room.filename_room])
                        for i in random_coords:
                            if i[0] == 4 and i[1] == 12:
                                # простая лазейка для того, чтобы мы посмотрели, как происходит коллизия
                                # Его не будет в конечном итоге
                                continue
                            barrel_group.add(Barrel(room.x + room.tile_size * i[0],
                                                    room.y + room.tile_size * i[1]))
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
                                    f'map{random.randrange(1, 4)}' if chest_room != count_room else 'room_with_chest')
                        if barrels_coords.get(room.filename_room):
                            random_coords = random.choice(barrels_coords[room.filename_room])
                            for i in random_coords:
                                if i[0] == 4 and i[1] == 12:
                                    # простая лазейка для того, чтобы мы посмотрели, как происходит коллизия
                                    # Его не будет в конечном итоге
                                    continue
                                barrel_group.add(Barrel(room.x + room.tile_size * i[0],
                                                        room.y + room.tile_size * i[1]))
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
        [i.move(x_move, y_move) for i in self.rooms]
        [i.move(x_move, y_move) for i in self.corridors]
        [i.move(x_move, y_move) for i in barrel_group]

    def update(self, screen):
        x, y = move()
        for room in self.rooms:
            if collide_rect(0, 0, others.WIDTH, others.HEIGHT,
                            room.x, room.y, room.x + room.width * room.tile_size,
                            room.y + room.height * room.tile_size):
                x, y = room.render(screen, x, y, player)
        for corridor in self.corridors:
            if collide_rect(0, 0, others.WIDTH, others.HEIGHT,
                            corridor.x, corridor.y, corridor.x + corridor.width * corridor.tile_size,
                            corridor.y + corridor.height * corridor.tile_size):
                x, y = corridor.render(screen, x, y, player)
        barrel_group.draw(screen)
        player.draw(screen)
        for room in self.rooms:
            if collide_rect(0, 0, others.WIDTH, others.HEIGHT,
                            room.x, room.y, room.x + room.width * room.tile_size,
                            room.y + room.height * room.tile_size):
                x, y = room.render_passing_walls(screen, x, y, player)
        for corridor in self.corridors:
            if collide_rect(0, 0, others.WIDTH, others.HEIGHT,
                            corridor.x, corridor.y, corridor.x + corridor.width * corridor.tile_size,
                            corridor.y + corridor.height * corridor.tile_size):
                corridor.render_passing_walls(screen, player)
        player.move()
        print(x, y, end=' ')
        for i in barrel_group:
            if not any([x, y]):
                break
            x, y = i.is_collide(player, x, y)
        print(x, y)
        if x or y:
            [i.move(x, y) for i in self.rooms]
            [i.move(x, y) for i in self.corridors]
            [i.move(x, y) for i in barrel_group]


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
    screen = pygame.display.set_mode(others.SIZE)
    # others.SIZE = others.WIDTH, others.HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
    # pygame.FULLSCREEN | pygame.DOUBLEBUF
    clock = pygame.time.Clock()

    running = 1

    player = Player()
    barrel_group = pygame.sprite.Group()

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
