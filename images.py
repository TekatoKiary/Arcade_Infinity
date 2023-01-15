import pygame
import os
import sys


def load_image_textures(name, colorkey=None):
    # Для папки текстурок отдельно
    fullname = os.path.join('textures', name)
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


def load_image(name, path='ui'):
    fullname = os.path.join(path, name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    return image


def cut_image(image, start_pos, size):
    return image.subsurface(pygame.Rect(start_pos, size))


# Player
player_image = load_image_textures('Adventurer\\stand\\adventurer_stand_0.png',
                                   -1)  # Изначальное изображение. Нужен для коллизии
player_image = pygame.transform.scale(player_image, (30, player_image.get_rect().height * 2.3))
player_images_stand = [load_image_textures(f'Adventurer\\stand\\adventurer_stand_{i}.png', -1)
                       for i in range(13)]  # спрайты игрока, когда он стоит
player_images_stand = [pygame.transform.scale(i, (30, player_image.get_height())) for i in player_images_stand]
player_images_move = [load_image_textures(f'Adventurer\\move\\adventurer_move_{i}.png', -1)
                      for i in range(8)]  # спрайты игрока, когда он идет куда-то
player_images_move = [pygame.transform.scale(i, (30, player_image.get_height())) for i in player_images_move]
# player_images_die = [load_image_textures(f'Adventurer\\die\\adventurer_die_{i}.png', -1) Хотели добавить
#                      for i in range(7)]  # спрайты игрока, когда умирает
# player_images_die = [pygame.transform.scale(i, (30, player_image.get_height())) for i in player_images_die]

# Monsters
ghoul_image = load_image_textures('Monsters\\Ghoul\\ghoul.png', -1)  # Изначальное изображение. Нужен для коллизии
ghoul_image = pygame.transform.scale(ghoul_image,
                                     (ghoul_image.get_rect().width * 2, ghoul_image.get_rect().height * 2.3))
ghoul_images_stand = [load_image_textures(f'Monsters\\Ghoul\\stand\\ghoul_stand_{i}.png', -1)
                      for i in range(4)]  # спрайты монстра, когда он стоит
ghoul_images_stand = \
    [pygame.transform.scale(i, (ghoul_image.get_rect().width, ghoul_image.get_rect().height))
     for i in ghoul_images_stand]
ghoul_images_move = [load_image_textures(f'Monsters\\Ghoul\\move\\ghoul_move_{i}.png', -1)
                     for i in range(8)]  # спрайты монстра, когда он двигается
ghoul_images_move = [
    pygame.transform.scale(i, (ghoul_image.get_rect().width, ghoul_image.get_rect().height))
    for i in ghoul_images_move]
ghoul_images_attack = [load_image_textures(f'Monsters\\Ghoul\\attack\\ghoul_attack_{i}.png', -1)
                       for i in range(6)]  # спрайты монстра, когда он атакует
ghoul_images_attack = [
    pygame.transform.scale(i, (ghoul_image.get_rect().width, ghoul_image.get_rect().height))
    for i in ghoul_images_attack]
ghoul_images_die = [load_image_textures(f'Monsters\\Ghoul\\die\\ghoul_die_{i}.png', -1)
                    for i in range(6)]  # спрайты монстра, когда он умирает
ghoul_images_die = [pygame.transform.scale(i, (ghoul_image.get_rect().width, ghoul_image.get_rect().height))
                    for i in ghoul_images_die]

zombie_image = cut_image(
    load_image('Monsters\\zombie old lady.png', 'textures'), (11, 0),
    (10, 16))  # Изначальное изображение. Нужен для коллизии
zombie_image = pygame.transform.scale(zombie_image,
                                      (zombie_image.get_rect().width * 2.5, zombie_image.get_rect().height * 3))
zombie_images_stand = [cut_image(
    load_image('Monsters\\zombie old lady.png', 'textures'), (11 + i * 32, 0), (10, 16)) for i in range(5)]
zombie_images_stand = \
    [pygame.transform.scale(i, (zombie_image.get_rect().width, zombie_image.get_rect().height))
     for i in zombie_images_stand]  # спрайты монстра, когда он стоит
zombie_images_move = [cut_image(
    load_image('Monsters\\zombie old lady.png', 'textures'), (11 + i * 32, 0), (10, 16)) for i in range(6, 11)]
zombie_images_move = [
    pygame.transform.scale(i, (zombie_image.get_rect().width, zombie_image.get_rect().height))
    for i in zombie_images_move]  # спрайты монстра, когда он двигается
zombie_images_die = [cut_image(
    load_image('Monsters\\zombie old lady.png', 'textures'), (716 + i * 32, 0), (10, 16)) for i in
    range(7)]
zombie_images_die = [
    pygame.transform.scale(i, (zombie_image.get_rect().width, zombie_image.get_rect().height))
    for i in zombie_images_die]  # спрайты монстра, когда он умирает
# Barrel
barrel_image = pygame.transform.scale(load_image_textures('barrel.png', -1), (28, 32))

# Spike
spike_images = [pygame.transform.scale(load_image_textures(f'Catacombs\\spike_{i}.png', -1), (32, 32)) for i in
                range(5)]
spike_images.extend([pygame.transform.scale(load_image_textures(f'Catacombs\\spike_{i}.png', -1), (32, 32))
                     for i in range(4, -1, -1)])

# Heal
heal_image = pygame.transform.scale(load_image_textures('heal.png', -1), (28, 32))

# Torch
torch_images = [pygame.transform.scale(load_image_textures(f'Catacombs\\torch_{i}.png', -1),
                                       (32 if 'torch_' != 'candleA_0' else 16, 32)) for i in range(1, 5)]
candlea_images = [pygame.transform.scale(load_image_textures(f'Catacombs\\candleA_0{i}.png', -1),
                                         (32 if 'candleA_0' != 'candleA_0' else 16, 32)) for i in range(1, 5)]
candleb_images = [pygame.transform.scale(load_image_textures(f'Catacombs\\candleB_0{i}.png', -1),
                                         (32 if 'candleB_0' != 'candleA_0' else 16, 32)) for i in range(1, 5)]

# Текстурки оружий:
GUN_TEXTURES = {
    'Transperent': pygame.Surface((5, 5), pygame.SRCALPHA, 32),
    'Ak47': cut_image(load_image(name='guns_outlined_free.png', path='textures'), (64, 31), (30, 15)),
    'Pistol': cut_image(load_image(name='guns_outlined_free.png', path='textures'), (49, 35), (14, 10)),
    'Uzi': cut_image(load_image(name='guns_outlined_free.png', path='textures'), (32, 93), (15, 18)),
    'Sniper': cut_image(load_image(name='guns_outlined_free.png', path='textures'), (96, 34), (32, 13)),
    'GrenadeLauncher': cut_image(load_image(name='guns_outlined_free.png', path='textures'), (64, 15), (26, 14)),
    'BallLightningLauncher': cut_image(load_image(name='guns_outlined_free.png', path='textures'), (99, 96), (17, 21)),
    'Infinity': cut_image(load_image(name='guns_outlined_free.png', path='textures'), (34, 50), (14, 12)),
    'MinePlacer': cut_image(load_image(name='guns_outlined_free.png', path='textures'), (0, 115), (6, 11)),
    'ThroughShooter': cut_image(load_image(name='guns_outlined_free.png', path='textures'), (32, 84), (22, 9)),
    'Shotgun': cut_image(load_image(name='guns_outlined_free.png', path='textures'), (0, 101), (31, 9)),
    'M4A4': cut_image(load_image(name='guns_outlined_free.png', path='textures'), (65, 67), (27, 13)),
}

# Текстуры пуль:
BULLET_TEXTURES = {
    'DefaultBullet': cut_image(load_image(name='bullets.png', path='textures'), (0, 0), (6, 10)),
    'DefaultBulletGray': cut_image(load_image(name='bullets.png', path='textures'), (8, 0), (6, 10)),
    'DefaultBulletGold': cut_image(load_image(name='bullets.png', path='textures'), (16, 0), (6, 10)),
    'DefaultBulletRustyCopper': cut_image(load_image(name='bullets.png', path='textures'), (24, 0), (6, 10)),
    'BallLightning': cut_image(load_image(name='bullets.png', path='textures'), (9, 12), (16, 16)),
    'LaserBullet': cut_image(load_image(name='bullets.png', path='textures'), (27, 12), (6, 14)),
    'Grenade': cut_image(load_image(name='bullets.png', path='textures'), (35, 12), (9, 9)),
    'Mine': cut_image(load_image(name='bullets.png', path='textures'), (46, 12), (15, 15)),
    'CircleBullet': cut_image(load_image(name='bullets.png', path='textures'), (0, 12), (7, 7)),
}