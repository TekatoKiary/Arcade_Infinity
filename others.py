import os
import sys
import pygame

# Функции и костанты
TILED_MAP_DIR = 'map\\ready_map'
SIZE = WIDTH, HEIGHT = 600, 600  # Вот эту строку лучше не импортировать через from, т.к. она в начале игры изменится,
# а в оптимизации нужно указывать точные размеры
FPS = 60

PICTURE_WAllS = [
    TILED_MAP_DIR + f'\\picture_wall{i}.tmx' for i in range(1, 9)
]
# Переделать(скорее всего)
barrels_coords = {'map1': [[]], 'map2': [[]], 'map3': [[]]}
# Пока только один вариант на каждую карту. Будет время добавлю другие
barrels_coords['map1'] += [[*((i, 13 - 1) for i in range(2, 42, 2)),
                            *((10, i - 1) for i in range(14, 30, 2)),
                            *((33, i - 1) for i in range(14, 30, 2)),
                            *((i, 30 - 1) for i in range(2, 42, 2)),
                            ]]

barrels_coords['map2'] += [[*((25, i - 1) for i in range(5, 19, 2)),
                            *((17, i - 1) for i in range(5, 19, 2)),
                            *((i, 18 - 1) for i in range(2, 17, 2)),
                            *((i, 18 - 1) for i in range(40, 25, -2)),
                            *((i, 25 - 1) for i in range(2, 17, 2)),
                            *((i, 25 - 1) for i in range(40, 25, -2)),
                            *((25, i - 1) for i in range(26, 43, 2)),
                            *((17, i - 1) for i in range(26, 43, 2)),
                            ]]

barrels_coords['map3'] += [[*((i, 15 - 1) for i in range(13, 30, 2)),
                            *((12, i - 1) for i in range(16, 31, 2)),
                            *((30, i - 1) for i in range(16, 31, 2)),
                            *((i, 32 - 1) for i in range(13, 30, 2)),
                            ]]


def load_image(name, colorkey=None):
    fullname = os.path.join('sprites', name)
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


def collide_rect(ax1, ay1, ax2, ay2, bx1, by1, bx2, by2):
    """Пересечение прямоугольников"""
    # Создан для оптимизации отрисовки комнат, то есть отрисовываются только те комнаты, которые находятся в экране,
    # а не за ним
    s1 = bx1 <= ax1 <= bx2 or bx1 <= ax2 <= bx2
    s2 = by1 <= ay1 <= by2 or by1 <= ay2 <= by2
    s3 = ax1 <= bx1 <= ax2 or ax1 <= bx2 <= ax2
    s4 = ay1 <= by1 <= ay2 or ay1 <= by2 <= ay2
    return True if ((s1 and s2) or (s3 and s4)) or ((s1 and s4) or (s3 and s2)) else False


def is_collide(player, image, x, y, x_speed, y_speed):
    # Можно сказать, создаем спрайт ячейки для проверки коллизии
    if any([x_speed, y_speed]):
        cell = pygame.sprite.Sprite()
        cell.image = image
        cell.rect = image.get_rect()
        cell.rect.y = y
        y_player = player.rect.y
        height = player.rect.height  # сохранить точность роста персонажа
        cell.rect.x = x - x_speed
        player.rect.y += player.rect.height // 1.01  # Мы смотрим коллизию по ногам, а не по телу
        player.rect.height -= player.rect.height // 1.01
        if pygame.sprite.collide_rect(cell, player):
            x_speed = 0
        cell.rect.x = x
        cell.rect.y -= y_speed
        if pygame.sprite.collide_rect(cell, player):
            y_speed = 0
        cell.kill()  # утечка памяти
        player.rect.height = height  # возвращаем как было
        player.rect.y = y_player
    return x_speed, y_speed
