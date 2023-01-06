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
        sprite.update_text(text=pl.balance)

def update_player_ammo(sprite):
        if pl.active_gun.is_reloading_now:
            sprite.update_text(text=f'reloading..')
        else:
            sprite.update_text(text=f'{pl.active_gun.ammo_amount} / {pl.active_gun.ammo}')

def open_shop():
    shop.set_visible(not shop.is_visible)
    shop.set_page(0)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Game')
    size = width, height = 800, 500  # скорее всего изменится
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    FPS = 60
    running = True

    # Основные спрайты
        # Список видов оружия: УЗИ, Снайперская винтовка, Автомат 
        # (несколько видов, например АК47, М4А4, какой-нибудь с цветными пулями), Пистолет, 
        # Автомат с рикошет-пулями, Гранатомет, Автомат с проходящими сквозь мобов пулями, 
        # Пушка, стреляющая шаровыми молниями, Пушка с маленьким уроном, но который наносится всех мобам
        # Расстановщик мин, Пушка с бесконечными патронами
    transperent_image = pygame.Surface((5, 5), pygame.SRCALPHA, 32)
    pl = sprites.Player((100, 100), '[image_name]')

    ak47_img = ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (64, 31), (30, 15))
    ak47 = sprites.Gun(player=pl, name='ak47', image=ak47_img, center_pos=(200, 200), ammo=999, damage=100, bullet_color=(255, 255, 255), bullet_size=(5, 20), fire_rate=150, shooting_accuracy=0.95)
    pistol_img = ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (49, 35), (14, 10))
    pistol = sprites.Gun(player=pl, name='pistol', center_pos=(300, 200), ammo=-1, image=pistol_img)

    fists = sprites.Gun(player=pl, name='fists', ammo=-1, target_group=sprites.player_sprite, damage=15, image=transperent_image, bullet_image=transperent_image)
    m1 = sprites.Monster(player=pl, center_pos=(300, 100), attack_range=50, image=ui.cut_image(ui.load_image(name='Ghoul Sprite Sheet.png', path='textures'), (3, 9), (27, 23)), gun=fists, player_avoidance=False, running_speed=70, move_randomly=False)
    m2 = sprites.Monster(player=pl, center_pos=(600, 100), image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1), (10, 15)))
    m3 = sprites.Monster(player=pl, center_pos=(650, 130), image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1), (10, 15)))
    m3 = sprites.Monster(player=pl, center_pos=(700, 160), image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1), (10, 15)))
    m3 = sprites.Monster(player=pl, center_pos=(650, 190), image=ui.cut_image(ui.load_image(name='zombie old lady.png', path='textures'), (11, 1), (10, 15)))

    # Ui
    fps = ui.Text(pos=(5, 5), sprite_group=sprites.all_sprites)
    player_info = ui.Img(pos=(20, 20), sprite_group=(sprites.all_sprites, sprites.ui_sprites), image_pos=(56, 0), image_size=(154, 48))
        # Переделать
    player_icon = pygame.transform.scale(pl.image, (pl.image.get_width() / 2, pl.image.get_height() / 2))
    player_info.image.blit(player_icon, (13, 12, pl.image.get_width(), pl.image.get_height()))
        # /\ /\ /\ /\ /\ /\
    player_hp_bar = ui.Img(pos=(20 + 54, 20 + 4), image_pos=(214, 0), image_size=(94, 18), sprite_group=(sprites.all_sprites, sprites.ui_sprites))
    shop_button = ui.Buttons(pos=(720, 20), sprite_group=(sprites.all_sprites, sprites.ui_sprites), image_pos=(192, 52), image_size=(60, 28))
    player_balance = ui.Text(pos=(90, 50), sprite_group=sprites.all_sprites)
    player_ammo = ui.Text(pos=(720, 460), sprite_group=sprites.all_sprites)
    info1 = ui.Text(pos=(30, 400), sprite_group=sprites.all_sprites, text='press W, A, S, D to move', size=14)
    info2 = ui.Text(pos=(30, 430), sprite_group=sprites.all_sprites, text='press F to take the gun', size=14)
    info2 = ui.Text(pos=(30, 460), sprite_group=sprites.all_sprites, text='press G to drop the gun', size=14)

    # Shop
    shop = ui.Shop(player=pl, pos=(590, 60), image_pos=(0, 84), image_size=(210, 312), sprite_group=(sprites.ui_sprites, sprites.all_sprites))

        # Тестовое добавление товаров в магазин
    Uzi_img = ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (32, 93), (15, 18))
    Uzi = ui.ShopItems(sprites.Gun(player=pl, name='Uzi', fire_rate=100, shooting_accuracy=0.6, damage=5, ammo=30, reload_time=2000, image=Uzi_img), 1)

    Sniper_img = ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (96, 34), (32, 13))
    Sniper = ui.ShopItems(sprites.Gun(player=pl, name='Sniper', fire_rate=2000, damage=100, ammo=20, reload_time=3000, bullet_color=(255, 128, 128), bullet_speed=600, image=Sniper_img), 1)
   
    GrenadeLauncher_img = ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (64, 15), (26, 14))
    GrenadeLauncher = ui.ShopItems(sprites.Gun(player=pl, name='GrenadeLauncher', fire_rate=1000, shooting_accuracy=0.8, damage=30, damage_type='splash', splash_damage=30, splash_radius=100, bullet_color=(64, 64, 196), image=GrenadeLauncher_img), 1)
   
    BallLightningLauncher_img = ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (99, 96), (17, 21))
    BallLightningLauncher = ui.ShopItems(sprites.Gun(player=pl, name='BallLightningLauncher', fire_rate=100, damage=100, ammo=1, reload_time=5000, destroy_bullets=False, bullet_color=(128, 128, 255), bullet_speed=50, bullet_size=(30, 30), image=BallLightningLauncher_img), 1)
  
    Infinity_img = ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (34, 50), (14, 12))
    Infinity = ui.ShopItems(sprites.Gun(player=pl, name='Infinity', fire_rate=300, damage=30, bullet_color=(196, 196, 64), ammo=-1, image=Infinity_img), 1)
    
    MinePlacer_img = ui.cut_image(ui.load_image(name='guns_outlined_free.png', path='textures'), (0, 115), (6, 11))
    MinePlacer = ui.ShopItems(sprites.Gun(player=pl, bullet_color=(196, 128, 64), damage=100, bullet_speed=0, ammo=1, reload_time=10, bullet_size=(20, 20), image=MinePlacer_img), 1)

    shop.add_item(Uzi, Sniper, GrenadeLauncher, BallLightningLauncher, Infinity, MinePlacer)
    # Респавн мобов для тестов
    respawn_monsters = pygame.USEREVENT + 3
    pygame.time.set_timer(respawn_monsters, 10000)

    while running:
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
                # ===============================================================================
                # Проверка нажатия на кнопку покупки
                for bg in shop.backgrounds:
                    if bg.mouse_clicked() and shop.is_visible and bg in sprites.all_sprites:
                        shop.buy_item(bg.item)
                if can_shoot:
                    pl.on_clicked(event)

                # Проверка нажатия на ячейки инвентаря
                for i, button in enumerate(pl.cells.buttons):
                    if button.mouse_clicked():
                        pl.switch_gun(i)
                # ===============================================================================
            
            if event.type == pygame.KEYDOWN:
                pl.on_k_pressed(event)
            
            # Перезарядка текущего оружия
            if event.type == pl.active_gun.reload_event:
                pl.active_gun.reload_ammo()
                pygame.time.set_timer(pl.active_gun.reload_event, 0)
                
            # Стрельба
            if event.type == pl.active_gun.shoot_event:
                if pygame.mouse.get_pressed()[0]:
                    pl.active_gun.shoot(target_pos=pygame.mouse.get_pos())
                else:
                    pygame.time.set_timer(pl.active_gun.shoot_event, 0)
                    pl.active_gun.can_shoot = True
            
            # Респавн мобов 
            # if event.type == respawn_monsters:
            #     for monster in sprites.dead_monsters:
            #         monster.respawn()

        pl.move()
        update_hp_bar(player_hp_bar, pl.hp_left / pl.max_hp)
        update_player_balance(player_balance)
        update_player_ammo(player_ammo)
        update_fps(fps)

        screen.fill((0, 0, 0))

        sprites.all_sprites.update()
        sprites.all_sprites.draw(screen)
        sprites.gun_sprites.update()
        

        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()