import pygame
import random
import time
import os
import others

pygame.init()  # инициализируем заранее чтобы не было проблем в sprites.py
pygame.display.set_caption('Arcade Infinity')
screen = pygame.display.set_mode(others.SIZE)


# others.SIZE = others.WIDTH, others.HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
# pygame.FULLSCREEN | pygame.DOUBLEBUF


# Главные цели:
# Сделать еще оптимизации
# class Heal
# Второстепенные цели:
# Добавить еще карты(это можно до бесконечности)
# Добавить еще вариации расстановок бочек, а вместе с ними и шипы(это можно до бесконечности)

# Шипы отображаются только в начале, так как в скором времени поменяется способ расстановки бочек и шипов

# Комната 704*704
# протяженность коридора различна: длина вертикального - 608, горизонтального - 576. Но с учетом особенностями
# соединении с комнатами они выравниваются

# Ключевой момент: карта представляет собой квадрат 4*4, в котором комнаты случайно выбирают свои координаты.
# Следовательно, с учетом коридоров между ними карта получается с длиной около 4500 и такой шириной.
# Тогда размер 4500*4500.
# Координаты относительно квадрата 4*4 нужны только для комнат и коридоров.
# Другие классы используют координаты относительно этих же комнат за исключением немногих

class Labyrinth:
    def __init__(self):
        self.rooms = []
        self.corridors = []
        self.create_rooms()
        print(*self.map_list, sep='\n')

    def create_rooms(self):
        loading()
        self.map_list = list([0] * 4 for _ in range(4))
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
                    room = Room(x, y, f'map{random.randrange(len(os.listdir(BAR_SPIKE_MAP_DIR)))}') \
                        if i < 2 else Room(x, y, f'end_room')
                    room.add_monsters()
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
                                    f'map{random.randrange(len(os.listdir(BAR_SPIKE_MAP_DIR)))}'
                                    if chest_room != count_room else 'room_with_chest')
                        room.add_monsters()
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
        [i.move(x_move, y_move) for i in torch_group]

    def update(self, screen):
        start_time = time.time()
        x, y = move()
        player.move(x, y)
        x, y = self.render(x, y)

        player.draw(screen)
        [i.draw(screen) for i in torch_group]

        x, y = self.render_passing_walls(x, y)

        x, y = self.collision_with_torches(x, y)

        if x or y:
            self.move_objects(x, y)
        # print("--- %s seconds ---" % (time.time() - start_time))

    def render(self, x, y):
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
        return x, y

    def render_passing_walls(self, x, y):
        for room in self.rooms:
            if collide_rect(0, 0, others.WIDTH, others.HEIGHT,
                            room.x, room.y, room.x + room.width * room.tile_size,
                            room.y + room.height * room.tile_size):
                x, y = room.render_passing_walls(screen, x, y, player)
                room.self_move_of_monster()
        for corridor in self.corridors:
            if collide_rect(0, 0, others.WIDTH, others.HEIGHT,
                            corridor.x, corridor.y, corridor.x + corridor.width * corridor.tile_size,
                            corridor.y + corridor.height * corridor.tile_size):
                corridor.render_passing_walls(screen, player)
        return x, y

    def collision_with_torches(self, x, y):
        for i in torch_group:
            if not any([x, y]):
                break
            x, y = i.is_collide(player, x, y)
        return x, y

    def move_objects(self, x, y):
        [i.move(x, y) for i in self.rooms]
        [i.move(x, y) for i in self.corridors]
        [i.move(x, y) for i in torch_group]

    def enter_next_level(self):
        room = self.rooms[3]
        if collide_rect(0, 0, others.WIDTH, others.HEIGHT,
                        room.x, room.y, room.x + room.width * room.tile_size,
                        room.y + room.height * room.tile_size) and room.enter_next_level(player):
            [i.clear() for i in self.rooms]
            self.rooms.clear()
            self.corridors.clear()
            [i.kill() for i in sprites.torch_group]
            [i.kill() for i in sprites.heal_group]
            self.create_rooms()


def loading():
    image = load_image('main_menu_bg2.png')
    image = pygame.transform.scale(image, (others.WIDTH, others.HEIGHT))
    screen.blit(image, (0, 0))
    font = pygame.font.Font('ui/MinimalPixel v2.ttf', 30).render('loading...', True, (255, 255, 255))
    screen.blit(font, (others.WIDTH - font.get_width() - 20, others.HEIGHT - font.get_height() - 20))
    pygame.display.update()


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
    import sprites
    from others import collide_rect, FPS, BAR_SPIKE_MAP_DIR, load_image
    from room import Room, Corridor
    from sprites import Player, torch_group, heal_group

    clock = pygame.time.Clock()

    running = 1

    player = Player()

    lab = Labyrinth()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if pygame.sprite.spritecollide(player, heal_group, True):
                        pass  # персонаж увеличивает здоровье
                    else:
                        lab.enter_next_level()
        screen.fill((0, 0, 0))
        lab.update(screen)
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()
