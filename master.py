import pygame
import ui
import sprites
import random



def update_fps(sprite):
    sprite.update_text(text=f'{clock.get_fps():2.0f}')

def update_hp_bar(bar, health_percent):
    size_delta = (1 - health_percent) * 94
    bar.update_image(image='main_ui.png', image_pos=(214 + size_delta, 0), image_size=(96 - size_delta, 18))

def update_player_balance(sprite):
        sprite.update_text(text=sprites.player_group.sprite.balance)

def update_player_ammo(sprite):
        if sprites.player_group.sprite.active_gun.is_reloading_now:
            sprite.update_text(text=f'reloading..')
        else:
            sprite.update_text(text=f'{sprites.player_group.sprite.active_gun.ammo_amount} / {sprites.player_group.sprite.active_gun.ammo}')

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

    # with open('stats/test.bin', 'rb') as test:





    player_stats = []
    map_stats = []

    pl = sprites.Player((100, 100), first_gun=GUNS['FirstGun'])

    m1 = sprites.Monster(center_pos=(300, 100), attack_range=50, image=ui.cut_image(ui.load_image(name='Ghoul Sprite Sheet.png', path='textures'), (3, 9), (27, 23)), gun=GUNS['Fists'], player_avoidance=False, running_speed=70, move_randomly=False)
    m2 = sprites.Monster(center_pos=(600, 100), image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1), (10, 15)))
    m3 = sprites.Monster(center_pos=(650, 130), image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1), (10, 15)))
    m3 = sprites.Monster(center_pos=(700, 160), image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1), (10, 15)))
    m3 = sprites.Monster(center_pos=(650, 190), image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1), (10, 15)))

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Game')
    size = width, height = 800, 500  # скорее всего изменится
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    FPS = 60
    running = True

    GUN_TEXTURES = {
        'Transperent': pygame.Surface((5, 5), pygame.SRCALPHA, 32),
        'Ak47': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (64, 31), (30, 15)),
        'Pistol': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (49, 35), (14, 10)),
        'Uzi': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (32, 93), (15, 18)),
        'Sniper': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (96, 34), (32, 13)),
        'GrenadeLauncher': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (64, 15), (26, 14)),
        'BallLightningLauncher': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (99, 96), (17, 21)),
        'Infinity': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (34, 50), (14, 12)),
        'MinePlacer': ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (0, 115), (6, 11))
    }

    GUNS = {
        'FirstGun': sprites.Gun(name='FirstGun', center_pos=(300, 200), ammo=-1, image=GUN_TEXTURES['Pistol'], is_raised=True, damage=30),
        'Ak47': sprites.Gun(name='Ak47', image=GUN_TEXTURES['Ak47'], center_pos=(200, 200), ammo=999, damage=100, bullet_color=(255, 255, 255), bullet_size=(5, 20), fire_rate=150, shooting_accuracy=0.95),
        'Pistol': sprites.Gun(name='pistol', center_pos=(300, 200), ammo=-1, image=GUN_TEXTURES['Pistol']),
        'Fists': sprites.Gun(name='Fists', ammo=-1, target_group=sprites.player_group, damage=15, image=GUN_TEXTURES['Transperent'], bullet_image=GUN_TEXTURES['Transperent']),
        'Uzi' : sprites.Gun(name='Uzi', fire_rate=100, shooting_accuracy=0.6, damage=5, ammo=30, reload_time=2000, image=GUN_TEXTURES['Uzi']),
        'Sniper': sprites.Gun(name='Sniper', fire_rate=2000, damage=100, ammo=20, reload_time=3000, bullet_color=(255, 128, 128), bullet_speed=600, image=GUN_TEXTURES['Sniper']),
        'GrenadeLauncher': sprites.Gun(name='GrenadeLauncher', fire_rate=1000, shooting_accuracy=0.8, damage=30, damage_type='splash', splash_damage=30, splash_radius=100, bullet_color=(64, 64, 196), image=GUN_TEXTURES['GrenadeLauncher']),
        'BallLightningLauncher': sprites.Gun(name='BallLightningLauncher', fire_rate=100, damage=100, ammo=1, reload_time=5000, destroy_bullets=False, bullet_color=(128, 128, 255), bullet_speed=50, bullet_size=(30, 30), image=GUN_TEXTURES['BallLightningLauncher']),
        'Infinity': sprites.Gun(name='Infinity', fire_rate=300, damage=30, bullet_color=(196, 196, 64), ammo=-1, image=GUN_TEXTURES['Infinity']),
        'MinePlacer': sprites.Gun(bullet_color=(196, 128, 64), damage=100, bullet_speed=0, ammo=1, reload_time=10, bullet_size=(20, 20), image=GUN_TEXTURES['MinePlacer'])
    }

    # Основные спрайты
        # Список видов оружия: УЗИ, Снайперская винтовка, Автомат 
        # (несколько видов, например АК47, М4А4, какой-нибудь с цветными пулями), Пистолет, 
        # Автомат с рикошет-пулями, Гранатомет, Автомат с проходящими сквозь мобов пулями, 
        # Пушка, стреляющая шаровыми молниями, Пушка с маленьким уроном, но который наносится всех мобам
        # Расстановщик мин, Пушка с бесконечными патронами
    init_sprites()
    give_gun(GUNS['Ak47'])
    
        # Ui
    fps = ui.Text(pos=(5, 5), sprite_group=sprites.all_sprites)
    player_info = ui.Img(pos=(20, 20), sprite_group=(sprites.all_sprites, sprites.ui_sprites), image_pos=(56, 0), image_size=(154, 48))
        # Переделать
    player_icon = pygame.transform.scale(sprites.player_group.sprite.image, (sprites.player_group.sprite.image.get_width() / 2, sprites.player_group.sprite.image.get_height() / 2))
    player_info.image.blit(player_icon, (13, 12, sprites.player_group.sprite.image.get_width(), sprites.player_group.sprite.image.get_height()))
        # /\ /\ /\ /\ /\ /\
    player_hp_bar = ui.Img(pos=(20 + 54, 20 + 4), image_pos=(214, 0), image_size=(94, 18), sprite_group=(sprites.all_sprites, sprites.ui_sprites))
    shop_button = ui.Buttons(pos=(720, 20), sprite_group=(sprites.all_sprites, sprites.ui_sprites), image_pos=(138, 52), image_size=(65, 28))
    player_balance = ui.Text(pos=(90, 50), sprite_group=sprites.all_sprites)
    player_ammo = ui.Text(pos=(720, 460), sprite_group=sprites.all_sprites)
    # Shop
    shop = ui.Shop(pos=(590, 60), image_pos=(0, 84), image_size=(210, 312), sprite_group=(sprites.ui_sprites, sprites.all_sprites))
        # Тестовое добавление товаров в магазин
    Uzi = ui.ShopItems(GUNS['Uzi'], 1)
    Sniper = ui.ShopItems(GUNS['Sniper'], 1)
    GrenadeLauncher = ui.ShopItems(GUNS['GrenadeLauncher'], 1)
    BallLightningLauncher = ui.ShopItems(GUNS['BallLightningLauncher'], 1)
    Infinity = ui.ShopItems(GUNS['Infinity'], 1)
    MinePlacer = ui.ShopItems(GUNS['MinePlacer'], 1)
    shop.add_item(Uzi, Sniper, GrenadeLauncher, BallLightningLauncher, Infinity, MinePlacer)
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

    pause_group = pygame.sprite.Group()
    main_menu_group = pygame.sprite.Group()
    loading_menu_sprites = pygame.sprite.Group()

    # Pause
    pause_button = ui.Buttons((390, 10), image_pos=(320, 44), image_size=(36, 36), sprite_group=(sprites.all_sprites, sprites.ui_sprites))

    black_bg = pygame.sprite.Sprite(pause_group)
    black_bg.image = pygame.Surface((1920, 1080), pygame.SRCALPHA, 32)
    black_bg.rect = black_bg.image.get_rect()
    black_bg.image.set_alpha(128)
    pygame.draw.rect(black_bg.image, (0, 0, 0), (0, 0, 1920, 1080))

    buttons_bg = ui.Img(pos=(280, 80), image_pos=(0, 400), image_size=(152, 132), sprite_group=(pause_group), scale=1.5)
    resume_button = ui.Buttons(pos=(345, 130), image_pos=(214, 216), image_size=(65, 28), sprite_group=(pause_group), scale=1.5)
    exit_button_on_pause = ui.Buttons(pos=(345, 180), image_pos=(214, 248), image_size=(65, 28), sprite_group=(pause_group), scale=1.5)
    info1 = ui.Text(pos=(30, 340), sprite_group=pause_group, text='press W, A, S, D to move', size=14)
    info2 = ui.Text(pos=(30, 370), sprite_group=pause_group, text='press F to take the gun', size=14)
    info3 = ui.Text(pos=(30, 400), sprite_group=pause_group, text='press G to drop the gun', size=14)
    info4 = ui.Text(pos=(30, 430), sprite_group=pause_group, text='press E to take the heal', size=14)
    info5 = ui.Text(pos=(30, 460), sprite_group=pause_group, text='press Enter to the next level', size=14)

    # Main menu
    main_menu_bg = ui.Img(pos=(0, 0), image='main_menu_bg2.png', image_pos=(0, 0), image_size=(800, 500), sprite_group=main_menu_group)

    start_game_button = ui.Buttons(pos=(345, 180), image_pos=(0, 52), image_size=(65, 28), sprite_group=(main_menu_group), scale=2)
    load_game_button = ui.Buttons(pos=(345, 240), image_pos=(69, 52), image_size=(65, 28), sprite_group=(main_menu_group), scale=2)
    exit_button_on_main_menu = ui.Buttons(pos=(345, 300), image_pos=(214, 248), image_size=(65, 28), sprite_group=(main_menu_group), scale=2)

    # Loading menu
    loading_menu_background = ui.Img(pos=(250, 110), image_pos=(0, 400), image_size=(152, 132), sprite_group=(loading_menu_sprites), scale=2)
    save2 = ui.Buttons(pos=(335, 150), image_pos=(214, 280), image_size=(65, 28), sprite_group=(loading_menu_sprites), scale=2)
    save1 = ui.Buttons(pos=(335, 210), image_pos=(214, 280), image_size=(65, 28), sprite_group=(loading_menu_sprites), scale=2)
    save3 = ui.Buttons(pos=(335, 270), image_pos=(214, 280), image_size=(65, 28), sprite_group=(loading_menu_sprites), scale=2)
    back_to_main_menu_button = ui.Buttons(pos=(335, 380), image_pos=(283, 280), image_size=(65, 28), sprite_group=(loading_menu_sprites), scale=2)



    game_started = False
    game_paused = False
    loading_menu_opened = False

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
                

            main_menu_group.draw(screen)

        elif game_paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if resume_button.mouse_clicked():
                        set_game_paused(False)
                    
                    if exit_button_on_pause.mouse_clicked():
                        set_game_paused(False)
                        set_game_started(False)
                        
            sprites.all_sprites.draw(screen)

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