import pygame
import random
import time
import os
import others

pygame.init()  # инициализируем заранее чтобы не было проблем в sprites.py
pygame.display.set_caption('Arcade Infinity')
screen = pygame.display.set_mode(others.SIZE)

import pygame
import ui
import sprites
import random
import pickle
import os


def update_fps(sprite):
    sprite.update_text(text=f'{clock.get_fps():2.0f}')


def update_hp_bar(bar, health_percent):
    size_delta = (1 - health_percent) * 94
    bar.update_image(image='main_ui.png', image_pos=(214 + size_delta, 0), image_size=(96 - size_delta, 18))

    if health_percent <= 0:
        set_game_over(True)


def update_player_balance(sprite):
    sprite.update_text(text=sprites.player_group.sprite.balance)


def update_player_ammo(sprite):
    if sprites.player_group.sprite.active_gun.is_reloading_now:
        sprite.update_text(text=f'reloading..')
    else:
        sprite.update_text(
            text=f'{sprites.player_group.sprite.active_gun.ammo_amount} / {sprites.player_group.sprite.active_gun.ammo}')


def open_shop():
    shop.set_visible(not shop.is_visible)
    shop.set_page(0)


def give_gun(gun):
    gun = gun.copy()
    gun.cord_x = sprites.player_group.sprite.cord_x
    gun.cord_y = sprites.player_group.sprite.cord_y
    sprites.player_group.sprite.take_gun()


def init_sprites():
    for sprite in sprites.entity_sprites:
        sprite.kill()
        sprites.all_sprites.remove(sprite)
        sprites.entity_sprites.remove(sprite)
        sprites.player_group.remove(sprite)
        sprites.gun_sprites.remove(sprite)
        sprites.monster_sprites.remove(sprite)
        sprites.collide_group.remove(sprite)
        sprites.bullet_group.remove(sprite)
        sprites.bar_sprites.remove(sprite)
        sprites.dead_monsters.remove(sprite)

    try:
        player_stats = game_load(current_save_id)
    except Exception:
        forced_save_update(current_save_id)
    player_inventory = [GUNS[gun] for gun in player_stats['player_inventory']]

    pl = sprites.Player((100, 100), inventory=player_inventory, hp_left=player_stats['player_hp'],
                        balance=player_stats['player_balance'])

    m1 = sprites.Monster(center_pos=(300, 100), attack_range=50,
                         image=ui.cut_image(ui.load_image(name='Ghoul Sprite Sheet.png', path='textures'), (3, 9),
                                            (27, 23)), gun=GUNS['Fists'], player_avoidance=False, running_speed=70,
                         move_randomly=False)
    m2 = sprites.Monster(center_pos=(600, 100),
                         image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1),
                                            (10, 15)), gun=GUNS['Pistol'])
    m3 = sprites.Monster(center_pos=(650, 130),
                         image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1),
                                            (10, 15)))
    m3 = sprites.Monster(center_pos=(700, 160),
                         image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1),
                                            (10, 15)))
    m3 = sprites.Monster(center_pos=(650, 190),
                         image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1),
                                            (10, 15)))


def forced_save_update(saveid):
    data = {}
    data['player_inventory'] = ['FirstGun', 'None', 'None']
    data['player_balance'] = 0
    data['player_hp'] = 100
    data['level'] = '1'
    with open(f"saves/save_{saveid}.bin", "wb") as fp:
        pickle.dump(data, fp)


# forced_save_update(3)

def game_save(saveid, set_to_default=False):
    if not set_to_default:
        data = {}
        data['player_inventory'] = list(
            (item.name if item != None else 'None') for item in sprites.player_group.sprite.inventory)
        data['player_balance'] = sprites.player_group.sprite.balance
        data['player_hp'] = sprites.player_group.sprite.hp_left
        data['level'] = '1'
        with open(f"saves/save_{saveid}.bin", "wb") as fp:
            pickle.dump(data, fp)
    else:
        data = {}
        data['player_inventory'] = ['FirstGun', 'None', 'None']
        data['player_balance'] = 0
        data['player_hp'] = 100
        data['level'] = '1'
        with open(f"saves/save_{saveid}.bin", "wb") as fp:
            pickle.dump(data, fp)


def game_load(saveid):
    with open(f"saves/save_{saveid}.bin", "rb") as fp:
        return pickle.load(fp)


def change_save(save_id):
    global current_save_id
    current_save_id = save_id


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Game')
    size = width, height = 800, 500  # скорее всего изменится
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    FPS = 60
    running = True

    current_save_id = 1

    GUN_TEXTURES = {
        'Transperent': pygame.Surface((5, 5), pygame.SRCALPHA, 32),
        'Ak47': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (64, 31), (30, 15)),
        'Pistol': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (49, 35), (14, 10)),
        'Uzi': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (32, 93), (15, 18)),
        'Sniper': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (96, 34), (32, 13)),
        'GrenadeLauncher': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (64, 15),
                                        (26, 14)),
        'BallLightningLauncher': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (99, 96),
                                              (17, 21)),
        'Infinity': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (34, 50), (14, 12)),
        'MinePlacer': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (0, 115), (6, 11)),
        'ThroughShooter': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (32, 84),
                                       (22, 9)),
        'Shotgun': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (0, 101), (31, 9)),
        'M4A4': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (65, 67), (27, 13)),
    }

    GUNS = {
        'None': None,
        'FirstGun': sprites.Gun(name='FirstGun', center_pos=(300, 200), ammo=-1, image=GUN_TEXTURES['Pistol'],
                                is_raised=True, damage=30),
        'Ak47': sprites.Gun(name='Ak47', image=GUN_TEXTURES['Ak47'], center_pos=(200, 200), ammo=999, damage=100,
                            bullet_color=(255, 255, 255), bullet_size=(5, 20), fire_rate=150, shooting_accuracy=0.95),
        'Pistol': sprites.Gun(name='pistol', center_pos=(300, 200), ammo=-1, image=GUN_TEXTURES['Pistol'], damage=10),
        'Fists': sprites.Gun(name='Fists', ammo=-1, target_group=sprites.player_group, damage=15,
                             image=GUN_TEXTURES['Transperent'], bullet_image=GUN_TEXTURES['Transperent']),
        'Uzi': sprites.Gun(name='Uzi', fire_rate=100, shooting_accuracy=0.6, damage=5, ammo=30, reload_time=2000,
                           image=GUN_TEXTURES['Uzi']),
        'Sniper': sprites.Gun(name='Sniper', fire_rate=2000, damage=100, ammo=20, reload_time=3000,
                              bullet_color=(255, 128, 128), bullet_speed=600, image=GUN_TEXTURES['Sniper']),
        'GrenadeLauncher': sprites.Gun(name='GrenadeLauncher', fire_rate=1000, shooting_accuracy=0.8, damage=30,
                                       damage_type='splash', splash_damage=30, splash_radius=100,
                                       bullet_color=(64, 64, 196), image=GUN_TEXTURES['GrenadeLauncher']),
        'BallLightningLauncher': sprites.Gun(name='BallLightningLauncher', fire_rate=100, damage=100, ammo=1,
                                             reload_time=5000, destroy_bullets=False, bullet_color=(128, 128, 255),
                                             bullet_speed=50, bullet_size=(30, 30),
                                             image=GUN_TEXTURES['BallLightningLauncher']),
        'Infinity': sprites.Gun(name='Infinity', fire_rate=300, damage=30, bullet_color=(196, 196, 64), ammo=-1,
                                image=GUN_TEXTURES['Infinity']),
        'MinePlacer': sprites.Gun(name='MinePlacer', bullet_color=(196, 128, 64), damage=100, bullet_speed=0, ammo=1,
                                  reload_time=10, bullet_size=(20, 20), image=GUN_TEXTURES['MinePlacer']),
        'ThroughShooter': sprites.Gun(name='ThroughShooter', bullet_color=(64, 64, 128), damage=2, ammo=30,
                                      reload_time=4000, image=GUN_TEXTURES['ThroughShooter'], destroy_bullets=False),
        'Shotgun': sprites.Shotgun(name='Shotgun', bullet_color=(64, 64, 128), damage=5, ammo=7, shooting_accuracy=0.7,
                                   reload_time=2000, image=GUN_TEXTURES['Shotgun'], fire_rate=500),
        'M4A4': sprites.Gun(name='M4A4', bullet_color=(128, 128, 128), damage=15, ammo=20, reload_time=3000,
                            image=GUN_TEXTURES['M4A4'], bullet_speed=350, fire_rate=230),
    }

    # Основные спрайты
    # Список видов оружия: УЗИ, Снайперская винтовка, Автомат
    # (несколько видов, например АК47, М4А4, какой-нибудь с цветными пулями), Пистолет,
    # Автомат с рикошет-пулями, Гранатомет, Автомат с проходящими сквозь мобов пулями,
    # Пушка, стреляющая шаровыми молниями, Пушка с маленьким уроном, но который наносится всех мобам
    # Расстановщик мин, Пушка с бесконечными патронами
    init_sprites()

    # Ui
    fps = ui.Text(pos=(5, 5), sprite_group=sprites.all_sprites)
    player_info = ui.Img(pos=(20, 20), sprite_group=(sprites.all_sprites, sprites.ui_sprites), image_pos=(56, 0),
                         image_size=(154, 48))
    # Переделать
    player_icon = pygame.transform.scale(sprites.player_group.sprite.image, (
    sprites.player_group.sprite.image.get_width() / 2, sprites.player_group.sprite.image.get_height() / 2))
    player_info.image.blit(player_icon, (
    13, 12, sprites.player_group.sprite.image.get_width(), sprites.player_group.sprite.image.get_height()))
    # /\ /\ /\ /\ /\ /\
    player_hp_bar = ui.Img(pos=(20 + 54, 20 + 4), image_pos=(214, 0), image_size=(94, 18),
                           sprite_group=(sprites.all_sprites, sprites.ui_sprites))
    shop_button = ui.Buttons(pos=(720, 20), sprite_group=(sprites.all_sprites, sprites.ui_sprites), image_pos=(138, 52),
                             image_size=(65, 28))
    player_balance = ui.Text(pos=(90, 50), sprite_group=sprites.all_sprites)
    player_ammo = ui.Text(pos=(720, 460), sprite_group=sprites.all_sprites)
    # Shop
    shop = ui.Shop(pos=(590, 60), image_pos=(0, 84), image_size=(210, 312),
                   sprite_group=(sprites.ui_sprites, sprites.all_sprites))
    # Тестовое добавление товаров в магазин
    Uzi = ui.ShopItems(GUNS['Uzi'], 1)
    Sniper = ui.ShopItems(GUNS['Sniper'], 1)
    GrenadeLauncher = ui.ShopItems(GUNS['GrenadeLauncher'], 1)
    BallLightningLauncher = ui.ShopItems(GUNS['BallLightningLauncher'], 1)
    Infinity = ui.ShopItems(GUNS['Infinity'], 1)
    MinePlacer = ui.ShopItems(GUNS['MinePlacer'], 1)
    ThroughShooter = ui.ShopItems(GUNS['ThroughShooter'], 1)
    Shotgun = ui.ShopItems(GUNS['Shotgun'], 1)
    FirstGun = ui.ShopItems(GUNS['FirstGun'], 1)
    M4A4 = ui.ShopItems(GUNS['M4A4'], 1)
    Ak47 = ui.ShopItems(GUNS['Ak47'], 1)
    shop.add_item(FirstGun, Uzi, Sniper, GrenadeLauncher, BallLightningLauncher, Infinity, MinePlacer, ThroughShooter,
                  Shotgun, M4A4, Ak47)
    # Респавн мобов для тестов
    respawn_monsters = pygame.USEREVENT + 3
    pygame.time.set_timer(respawn_monsters, 10000)


    # ================================================================

    def set_game_paused(bool):
        global game_paused
        if bool:
            game_paused = True
            for sprite in pause_group:
                sprite.add(sprites.all_sprites)
        else:
            game_paused = False
            for sprite in pause_group:
                sprites.all_sprites.remove(sprite)


    def set_game_started(bool):
        global game_started
        if bool:
            game_started = True
            for sprite in main_menu_group:
                sprite.kill()
                sprite.add(main_menu_group)
        else:
            game_started = False

        init_sprites()


    def set_loading_menu_opened(bool):
        global loading_menu_opened
        if bool:
            loading_menu_opened = True
            for sprite in loading_menu_sprites:
                sprite.add(main_menu_group)
        else:
            loading_menu_opened = False
            for sprite in loading_menu_sprites:
                main_menu_group.remove(sprite)


    def set_game_over(bool):
        global game_over
        if bool:
            game_over = True
            for sprite in game_over_sprites:
                sprite.add(sprites.all_sprites)
        else:
            game_over = False
            for sprite in game_over_sprites:
                sprites.all_sprites.remove(sprite)


    pause_group = pygame.sprite.Group()
    main_menu_group = pygame.sprite.Group()
    loading_menu_sprites = pygame.sprite.Group()
    game_over_sprites = pygame.sprite.Group()

    # Pause
    pause_button = ui.Buttons((390, 10), image_pos=(320, 44), image_size=(36, 36),
                              sprite_group=(sprites.all_sprites, sprites.ui_sprites))

    black_bg = pygame.sprite.Sprite(pause_group)
    black_bg.image = pygame.Surface((1920, 1080), pygame.SRCALPHA, 32)
    black_bg.rect = black_bg.image.get_rect()
    black_bg.image.set_alpha(128)
    pygame.draw.rect(black_bg.image, (0, 0, 0), (0, 0, 1920, 1080))

    buttons_bg = ui.Img(pos=(280, 80), image_pos=(0, 400), image_size=(152, 132), sprite_group=(pause_group), scale=1.5)
    resume_button = ui.Buttons(pos=(345, 130), image_pos=(214, 216), image_size=(65, 28), sprite_group=(pause_group),
                               scale=1.5)
    exit_button_on_pause = ui.Buttons(pos=(345, 180), image_pos=(214, 248), image_size=(65, 28),
                                      sprite_group=(pause_group), scale=1.5)
    info1 = ui.Text(pos=(30, 340), sprite_group=pause_group, text='press W, A, S, D to move', size=14)
    info2 = ui.Text(pos=(30, 370), sprite_group=pause_group, text='press F to take the gun', size=14)
    info3 = ui.Text(pos=(30, 400), sprite_group=pause_group, text='press G to drop the gun', size=14)
    info4 = ui.Text(pos=(30, 430), sprite_group=pause_group, text='press E to take the heal', size=14)
    info5 = ui.Text(pos=(30, 460), sprite_group=pause_group, text='press Enter to the next level', size=14)

    # Main menu
    main_menu_bg = ui.Img(pos=(0, 0), image='main_menu_bg2.png', image_pos=(0, 0), image_size=(800, 500),
                          sprite_group=main_menu_group)

    start_game_button = ui.Buttons(pos=(345, 180), image_pos=(0, 52), image_size=(65, 28),
                                   sprite_group=(main_menu_group), scale=2)
    load_game_button = ui.Buttons(pos=(345, 240), image_pos=(69, 52), image_size=(65, 28),
                                  sprite_group=(main_menu_group), scale=2)
    exit_button_on_main_menu = ui.Buttons(pos=(345, 300), image_pos=(214, 248), image_size=(65, 28),
                                          sprite_group=(main_menu_group), scale=2)
    current_save = ui.Text(pos=(385, 150), text=f"save {current_save_id}", sprite_group=(main_menu_group), size=14)

    # Loading menu
    loading_menu_background = ui.Img(pos=(250, 110), image_pos=(0, 400), image_size=(152, 132),
                                     sprite_group=(loading_menu_sprites), scale=2)
    save1 = ui.Buttons(pos=(335, 150), image_pos=(214, 280), image_size=(65, 28), sprite_group=(loading_menu_sprites),
                       scale=2)
    save2 = ui.Buttons(pos=(335, 210), image_pos=(214, 312), image_size=(65, 28), sprite_group=(loading_menu_sprites),
                       scale=2)
    save3 = ui.Buttons(pos=(335, 270), image_pos=(214, 344), image_size=(65, 28), sprite_group=(loading_menu_sprites),
                       scale=2)
    back_to_main_menu_button = ui.Buttons(pos=(335, 380), image_pos=(283, 280), image_size=(65, 28),
                                          sprite_group=(loading_menu_sprites), scale=2)

    # game lost
    red_bg = pygame.sprite.Sprite(game_over_sprites)
    red_bg.image = pygame.Surface((1920, 1080), pygame.SRCALPHA, 32)
    red_bg.rect = black_bg.image.get_rect()
    red_bg.image.set_alpha(128)
    pygame.draw.rect(red_bg.image, (64, 0, 0), (0, 0, 1920, 1080))

    restart_button = ui.Buttons(pos=(340, 210), image_pos=(283, 216), image_size=(65, 28),
                                sprite_group=(game_over_sprites), scale=1.5)
    exit_button_on_game_over = ui.Buttons(pos=(340, 255), image_pos=(214, 248), image_size=(65, 28),
                                          sprite_group=(game_over_sprites), scale=1.5)
    gameovertext = ui.Text(pos=(200, 120), sprite_group=game_over_sprites, text='GAME OVER', size=64)

    game_started = False
    game_paused = False
    loading_menu_opened = False
    game_over = False

    set_game_started(False)

    while running:
        if not game_started:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not loading_menu_opened:
                        if start_game_button.mouse_clicked():
                            set_game_started(True)
                        if exit_button_on_main_menu.mouse_clicked():
                            running = False
                        if load_game_button.mouse_clicked():
                            set_loading_menu_opened(True)
                    else:
                        if back_to_main_menu_button.mouse_clicked():
                            set_loading_menu_opened(False)
                        if save1.mouse_clicked():
                            change_save(1)
                            set_loading_menu_opened(False)
                        if save2.mouse_clicked():
                            change_save(2)
                            set_loading_menu_opened(False)
                        if save3.mouse_clicked():
                            change_save(3)
                            set_loading_menu_opened(False)
            current_save.update_text(f"save {current_save_id}")
            main_menu_group.draw(screen)

        elif game_paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if resume_button.mouse_clicked():
                        set_game_paused(False)

                    if exit_button_on_pause.mouse_clicked():
                        game_save(current_save_id)
                        set_game_paused(False)
                        set_game_started(False)
                        shop.set_visible(False)

            sprites.all_sprites.draw(screen)

        elif game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_button_on_game_over.mouse_clicked():
                        set_game_paused(False)
                        set_game_started(False)
                        set_game_over(False)
                        shop.set_visible(False)
                    if restart_button.mouse_clicked():
                        game_save(current_save_id, True)
                        init_sprites()
                        set_game_over(False)
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    can_shoot = True
                    # ===============================================================================
                    for sprite in sprites.ui_sprites:
                        # Если навелся на UI, то стрелять нельзя
                        if sprite.mouse_hovered():
                            can_shoot = False
                            # Открыть магазин
                            if shop_button.mouse_clicked():
                                open_shop()
                            # Листать страницы магазина
                            if shop.button_back.mouse_clicked() or shop.button_next.mouse_clicked():
                                shop.flip_shop_page()
                            # Поставить игру на паузу
                            if pause_button.mouse_clicked():
                                set_game_paused(True)
                    # ===============================================================================
                    # Проверка нажатия на кнопку покупки
                    for bg in shop.backgrounds:
                        if bg.mouse_clicked() and shop.is_visible and bg in sprites.all_sprites:
                            shop.buy_item(bg.item)

                    if can_shoot:
                        sprites.player_group.sprite.on_clicked(event)

                    # Проверка нажатия на ячейки инвентаря
                    for i, button in enumerate(sprites.player_group.sprite.cells.buttons):
                        if button.mouse_clicked():
                            sprites.player_group.sprite.switch_gun(i)
                    # ===============================================================================

                if event.type == pygame.KEYDOWN:
                    sprites.player_group.sprite.on_k_pressed(event)

                # Перезарядка текущего оружия
                if event.type == sprites.player_group.sprite.active_gun.reload_event:
                    sprites.player_group.sprite.active_gun.reload_ammo()
                    pygame.time.set_timer(sprites.player_group.sprite.active_gun.reload_event, 0)

                # Стрельба
                if event.type == sprites.player_group.sprite.active_gun.shoot_event:
                    if pygame.mouse.get_pressed()[0]:
                        sprites.player_group.sprite.active_gun.shoot(target_pos=pygame.mouse.get_pos())
                    else:
                        pygame.time.set_timer(sprites.player_group.sprite.active_gun.shoot_event, 0)
                        sprites.player_group.sprite.active_gun.can_shoot = True

                # Респавн мобов
                # if event.type == respawn_monsters:
                #     for monster in sprites.dead_monsters:
                #         monster.respawn()

            sprites.player_group.sprite.move()
            update_hp_bar(player_hp_bar, sprites.player_group.sprite.hp_left / sprites.player_group.sprite.max_hp)
            update_player_balance(player_balance)
            update_player_ammo(player_ammo)
            update_fps(fps)

            screen.fill((0, 0, 0))

            sprites.all_sprites.update()
            sprites.all_sprites.draw(screen)
            sprites.gun_sprites.update()

        pygame.display.update()
        clock.tick(60)

    pygame.quit()

import pygame
import random
import time
import os
import others

pygame.init()  # инициализируем заранее чтобы не было проблем в sprites.py
pygame.display.set_caption('Arcade Infinity')
screen = pygame.display.set_mode(others.SIZE)

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
        self.cnt_level = 0

        self.create_rooms()
        print(*self.map_list, sep='\n')

    def create_rooms(self):
        loading()
        self.cnt_level += 1
        self.text_level = f'Level {self.cnt_level}'
        self.color = pygame.Color(255, 255, 255)  # его нужно менять потом
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

        Heal(room.x + 5 * room.tile_size, room.y + 5 * room.tile_size)
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
        [i.move(x_move, y_move) for i in heal_group]

    def update(self, screen):
        start_time = time.time()
        x, y = move()
        player.move(x, y)
        x, y = self.render(x, y)
        sprites.heal_group.draw(screen)
        player.draw(screen)
        [i.draw(screen) for i in torch_group]

        x, y = self.render_passing_walls(x, y)

        x, y = self.collision_with_torches(x, y)

        hsv = self.color.hsva
        if hsv[2] >= 10:
            self.color.hsva = (hsv[0], hsv[1], hsv[2] - 1, hsv[3])
            self.show_level()

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
        [i.move(x, y) for i in heal_group]

    def enter_next_level(self):
        room = self.rooms[3]
        if collide_rect(0, 0, others.WIDTH, others.HEIGHT,
                        room.x, room.y, room.x + room.width * room.tile_size,
                        room.y + room.height * room.tile_size) and room.enter_next_level(player):
            [i.clear() for i in self.rooms]
            self.rooms.clear()
            self.corridors.clear()
            [i.kill() for i in sprites.torch_group]
            # [i.kill() for i in sprites.heal_group]
            self.create_rooms()

    def show_level(self):
        font = pygame.font.Font('ui/MinimalPixel v2.ttf', 30).render(self.text_level, True, self.color)
        screen.blit(font, (others.WIDTH // 2 - font.get_width() // 2, 150))


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
    from sprites import Player, torch_group, heal_group, Heal

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
                    heal = pygame.sprite.spritecollide(player, heal_group, False)
                    if heal:
                        heal[0].heal()  # персонаж увеличивает здоровье
                if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                    lab.enter_next_level()
        screen.fill((0, 0, 0))
        lab.update(screen)
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()
