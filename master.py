import pygame
import random
import ui
import sprites


def update_hp_bar(bar, health_percent):
    size_delta = (1 - health_percent) * 94
    bar.update_image(image='main_ui.png', image_pos=(214 + size_delta, 0), image_size=(96 - size_delta, 18))

def update_player_balance(sprite):
        sprite.update_text(text=pl.balance)

def update_player_ammo(sprite):
    if pl.active_gun != 'Hands':
        if pl.active_gun.is_reloading_now:
            sprite.update_text(text=f'reloading..')
        else:
            sprite.update_text(text=f'{pl.active_gun.ammo_amount} / {pl.active_gun.ammo}')
    else:
        sprite.update_text(text='0 / 0')

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
    pl = sprites.Player((100, 100), '[image_name]')
    gun = sprites.Gun(player=pl, center_pos=(200, 200), image='[image_name]', ammo=999, damage=10, bullet_color=(255, 255, 255), bullet_size=(5, 20), fire_rate=150, shooting_accuracy=0.95, damage_type='splash', splash_damage=10, splash_radius=50)
    gun2 = sprites.Gun(player=pl, center_pos=(300, 200), image='[image_name]', ammo=-1, reload_time=1000, damage_type='splash', splash_damage=100, splash_radius=500)
    m1 = sprites.Monster(player=pl, center_pos=(300, 100), image='[image_name]')
    m2 = sprites.Monster(player=pl, center_pos=(400, 100), image='[image_name]', hp=1)
    m3 = sprites.Monster(player=pl, center_pos=(450, 130), image='[image_name]', hp=1)
    m4 = sprites.Monster(player=pl, center_pos=(470, 170), image='[image_name]', hp=1)
    m5 = sprites.Monster(player=pl, center_pos=(450, 210), image='[image_name]', hp=1)
    # Ui
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
    for _ in range(25):
        gun = sprites.Gun(player=pl, bullet_color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        item = ui.ShopItems(gun, random.randint(1, 3))
        shop.add_item(item)

    # Респавн мобов для тестов
    respawn_monsters = pygame.USEREVENT + 3
    pygame.time.set_timer(respawn_monsters, 30)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEMOTION:
                pass

            if event.type == pygame.MOUSEBUTTONDOWN:
                can_shoot = True
                for sprite in sprites.ui_sprites:
                    # Если навелся на UI, то стрелять нельзя
                    if sprite.mouse_hovered():
                        can_shoot = False

                        if shop_button.mouse_clicked():
                            open_shop()
                        
                        # Листать страницы магазина
                        if shop.button_back.mouse_clicked() or shop.button_next.mouse_clicked():
                            shop.flip_shop_page()

                
                # Проверка нажатия на кнопку покупки
                for bg in shop.backgrounds:
                    if bg.mouse_clicked() and shop.is_visible and bg in sprites.all_sprites:
                        shop.buy_item(bg.item)
                        
                if can_shoot:
                    pl.on_clicked(event)
            
            if event.type == pygame.KEYDOWN:
                pl.on_k_pressed(event)
            
            if pl.active_gun != 'Hands':
                if event.type == pl.active_gun.reload_event:
                    pl.active_gun.reload_ammo()
                    pygame.time.set_timer(pl.active_gun.reload_event, 0)
                
                if event.type == pl.active_gun.shoot_event:
                    if pygame.mouse.get_pressed()[0]:
                        pl.active_gun.shoot()
                    else:
                        pygame.time.set_timer(pl.active_gun.shoot_event, 0)
                        pl.active_gun.can_shoot = True
            
            if event.type == respawn_monsters:
                for monster in sprites.dead_monsters:
                    monster.respawn()

        pl.move()
        update_hp_bar(player_hp_bar, pl.hp_left / pl.max_hp)
        update_player_balance(player_balance)
        update_player_ammo(player_ammo)

        screen.fill((0, 0, 0))

        sprites.all_sprites.update()
        sprites.all_sprites.draw(screen)

        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()