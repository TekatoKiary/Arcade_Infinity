import os
import sys
import pygame

# Функции и костанты
TILED_MAP_DIR = 'map\\ready_map'
SIZE = WIDTH, HEIGHT = 600, 600
FPS = 60


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
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
