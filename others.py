import os
import pygame

# Функции и костанты
TILED_MAP_DIR = 'map'
BAR_SPIKE_MAP_DIR = 'map\\barrels_and_spike'

SIZE = WIDTH, HEIGHT = 600, 600  # Вот эту строку лучше не импортировать через from, т.к. она в начале игры изменится,
# а в оптимизации нужно указывать точные размеры
FPS = 60

PICTURE_WAllS = [TILED_MAP_DIR + f'\\picture_wall\\picture_wall{i}.tmx' for i in range(1, 9)]  # Рисунки на стене


def load_image(name, path='ui'):
    fullname = os.path.join(path, name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
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


def is_collide_with_speed(player, image, x, y, x_speed, y_speed):
    if any([x_speed, y_speed]):
        # Можно сказать, создаем спрайт ячейки для проверки коллизии
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


def is_collide(player, image, x, y, change_player=True):
    # Можно сказать, создаем спрайт ячейки для проверки коллизии
    cell = pygame.sprite.Sprite()
    cell.image = image
    cell.rect = image.get_rect()
    cell.rect.y = y

    y_player = player.rect.y
    height = player.rect.height  # сохранить точность роста персонажа
    cell.rect.x = x
    if change_player:  # он понадобится в одном месте
        player.rect.y += player.rect.height // 1.01  # Мы смотрим коллизию по ногам, а не по телу
        player.rect.height -= player.rect.height // 1.01
    t = False
    if pygame.sprite.collide_rect(cell, player):
        t = True
    player.rect.height = height  # возвращаем как было
    player.rect.y = y_player
    cell.kill()
    return t
