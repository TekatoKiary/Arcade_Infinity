import pygame
import os
import random
import math
import time
import ui
import copy


class Hands(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)

        self.rect = (0, 0, 0, 0)
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA, 32)

    def try_shoot(self):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, center_pos=(0, 0), image=None, max_hp=100):
        super().__init__(all_sprites)
        self.add(player_sprite)

        self.max_hp = max_hp
        self.hp_left = self.max_hp

        self.active_gun = Hands()

        self.image = pygame.Surface((50, 50), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, (128, 0, 255), (0, 0, 50, 50), 0)

        self.rect.x = center_pos[0] - self.image.get_width() // 2
        self.rect.y = center_pos[1] - self.image.get_height() // 2

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

        self.balance = 10
    
    def take_damage(self, damage):
        self.hp_left -= damage

    def on_clicked(self, event):
        if event.button == 1:
            self.active_gun.try_shoot()
    
    def on_k_pressed(self, event):
        if event.key == pygame.K_g:
            self.drop_gun()
        if event.key == pygame.K_f:
            self.take_gun()


    def take_gun(self):
        for gun in gun_sprites:
            if self.active_gun.__class__.__name__ == 'Hands':
                if pygame.sprite.spritecollide(gun, player_sprite, False):
                    if gun.can_be_raised:
                        gun.is_raised = True
                        self.active_gun = gun
            
    def drop_gun(self):
        if self.active_gun.__class__.__name__ != 'Hands':
            self.active_gun.is_raised = False
            self.active_gun.is_reloading_now = False
            pygame.time.set_timer(self.active_gun.reload_event, 0)
            self.active_gun.can_shoot = True
            pygame.time.set_timer(self.active_gun.shoot_event, 0)
            self.active_gun = Hands()

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.cord_y -= 80 / 60
        if keys[pygame.K_a]:
            self.cord_x -= 80 / 60
        if keys[pygame.K_s]:
            self.cord_y += 80 / 60
        if keys[pygame.K_d]:
            self.cord_x += 80 / 60
    
    def give_money(self, reward):
        self.balance += reward

    def update(self):
        self.rect.x = self.cord_x
        self.rect.y = self.cord_y


class Gun(pygame.sprite.Sprite):
    def __init__(self, name='gun', center_pos=(0, 0), image='', destroy_bullets=True, damage_type='point', bullet_color=(128, 128, 128), \
        bullet_size=(10, 10), bullet_speed=300, fire_rate=300, shooting_accuracy=1, damage=0, splash_damage=0, splash_radius=0, ammo=10, \
            reload_time=3000, reload_event=1, shoot_event=2):

        super().__init__()
        self.add(gun_sprites, all_sprites)

        self.name = name

        # Их не изменять
        self.center_pos = center_pos
        self.destroy_bullets = destroy_bullets
        self.bullet_color = bullet_color
        self.bullet_size = bullet_size
        self.bullet_speed = bullet_speed
        self.damage_type = damage_type
        self.damage = damage
        self.splash_damage = splash_damage
        self.splash_radius = splash_radius
        self.ammo = ammo
        self.fire_rate = fire_rate
        self.shooting_accuracy = shooting_accuracy

        self.ammo_amount = self.ammo
        self.reload_time = reload_time

        self.reload_event_num = reload_event
        self.reload_event = pygame.USEREVENT + reload_event
        self.shoot_event_num = shoot_event
        self.shoot_event = pygame.USEREVENT + shoot_event

        self.image = pygame.Surface((25, 25), pygame.SRCALPHA, 32)
        self.rotate_image = self.image
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, (128, 255, 128), (0, 0, 25, 25), 0)

        self.rect.x = center_pos[0] - self.rotate_image.get_width() / 2
        self.rect.y = center_pos[1] - self.rotate_image.get_height() / 2

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

        self.can_be_raised = True
        self.is_raised = False
        self.is_reloading_now = False
        self.can_shoot = True
        

    def try_shoot(self):
        if self.can_shoot:
            if pl.active_gun.__class__.__name__ != 'Hands':
                self.shoot()
                self.can_shoot = False
                pygame.time.set_timer(self.shoot_event, self.fire_rate)
    
    def shoot(self):
        if not self.is_reloading_now:
            if self.ammo_amount > 0:
                self.ammo_amount -= 1
                Bullet(pl.active_gun, (self.cord_x, self.cord_y), pygame.mouse.get_pos())
            else:
                self.is_reloading_now = True
                pygame.time.set_timer(self.reload_event, self.reload_time)
    
    def reload_ammo(self):
        self.is_reloading_now = False
        self.ammo_amount += self.ammo

    def rotate(self):
        self.image = pygame.transform.rotate(
            self.rotate_image, self.math_angle())

    def math_angle(self):
        rel_x, rel_y = pygame.mouse.get_pos()[0] - self.cord_x - \
            self.rotate_image.get_width() / 2, pygame.mouse.get_pos()[1] - \
            self.cord_y - self.rotate_image.get_height() / 2
        angle = (180 / math.pi) * math.atan2(rel_x, rel_y)
        return angle

    def update(self):
        self.rect.x = self.cord_x
        self.rect.y = self.cord_y

        if self.is_raised:
            pl.active_gun = self
            self.cord_x = pl.cord_x + 30
            self.cord_y = pl.cord_y + 20

            self.rotate()
    
    def copy(self):
        return Gun(name=self.name, center_pos=self.center_pos, image=self.image, destroy_bullets=self.destroy_bullets, \
            damage_type=self.damage_type, bullet_color=self.bullet_color, bullet_size=self.bullet_size, bullet_speed=self.bullet_speed, \
                fire_rate=self.fire_rate, shooting_accuracy=self.shooting_accuracy, damage=self.damage, splash_damage=self.splash_damage, \
                    splash_radius=self.splash_radius, ammo=self.ammo, reload_time=self.reload_time, reload_event=self.reload_event_num, \
                        shoot_event=self.shoot_event_num)


class Bullet(pygame.sprite.Sprite):
    # damage_type: point, splash
    def __init__(self, gun, cords_from=(0, 0), cords_to=(0, 0)):
        super().__init__(all_sprites)
        self.add(bullet_group)

        self.gun = gun
        self.cords_from = cords_from
        self.cords_to = cords_to

        self.cords = [self.cords_from[0], self.cords_from[1]]

        self.image = pygame.Surface((self.gun.bullet_size[0], self.gun.bullet_size[1]), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.x = self.cords_from[0]
        self.rect.y = self.cords_from[1]
        pygame.draw.rect(self.image, self.gun.bullet_color, (0, 0, self.gun.bullet_size[0], self.gun.bullet_size[1]), 0)

        self.vx, self.vy = self.math_speed()
        self.rotate()

    def math_angle(self):
        rel_x, rel_y = self.randomized_mouse_cord_x - self.rect.x - \
            self.gun.bullet_size[0] / 2, self.randomized_mouse_cord_y - \
            self.rect.y - self.gun.bullet_size[1] / 2
        angle = (180 / math.pi) * math.atan2(rel_x, rel_y)
        return angle
    
    def rotate(self):
        self.image = pygame.transform.rotate(self.image, self.math_angle())

    def math_speed(self):
        self.randomized_mouse_cord_x = self.cords_to[0] + random.choice([-1, 1]) * \
            random.uniform(0, (1 - self.gun.shooting_accuracy)) * self.cords_to[0]

        self.randomized_mouse_cord_y = self.cords_to[1] + random.choice([-1, 1]) * \
            random.uniform(0, (1 - self.gun.shooting_accuracy)) * self.cords_to[1]

        rel_x = self.randomized_mouse_cord_x - self.cords_from[0] - self.image.get_width() / 2
        rel_y = self.randomized_mouse_cord_y - self.cords_from[1] - self.image.get_height() / 2


        vx = round(rel_x / math.sqrt(rel_x ** 2 + rel_y ** 2) * self.gun.bullet_speed, 2)
        vy = round(rel_y / math.sqrt(rel_x ** 2 + rel_y ** 2) * self.gun.bullet_speed, 2)
        return (vx, vy)

    def move(self):
        self.cords[0] += self.vx / 60
        self.cords[1] += self.vy / 60

    def collision_handling(self):
        colides = pygame.sprite.groupcollide(bullet_group, collide_group, self.gun.destroy_bullets, False)
        for bullet, sprites in colides.items():
            for sprite in sprites:
                sprite.hp_left -= bullet.gun.damage

    
    def optimize(self):
        if not 0 < self.cords[0] < 800 or \
            not 0 < self.cords[1] < 500:
                self.kill()


    def update(self):
        self.move()

        self.rect.x = self.cords[0]
        self.rect.y = self.cords[1]

        self.optimize()
        self.collision_handling()


class Monster(pygame.sprite.Sprite):
    def __init__(self, center_pos, image, hp=100, reward=1):
        super().__init__(all_sprites)
        self.add(monster_sprites)
        self.add(collide_group)

        self.active_gun = Hands()

        self.max_hp = hp
        self.reward = reward
        self.hp_left = self.max_hp

        self.hp_bar = Bars(owner=self, max_hp=self.max_hp)

        self.image = pygame.Surface((30, 30), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()

        pygame.draw.rect(self.image, (64, 0, 128), (0, 0, 30, 60), 0)

        self.rect.x = center_pos[0] - self.image.get_width() // 2
        self.rect.y = center_pos[1] - self.image.get_height() // 2

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def respawn(self):
        self.hp_left = self.max_hp
        self.add(all_sprites, collide_group, monster_sprites)
        dead_monsters.remove(self)
        self.hp_bar.add(all_sprites, bar_sprites)
    
    def die(self):
        self.kill()
        self.add(dead_monsters)
    
    def give_reward(self):
        pl.give_money(self.reward)

    def update(self):
        if self.hp_left <= 0:
            self.die()
            self.give_reward()

        self.rect.x = self.cord_x
        self.rect.y = self.cord_y


class Bars(pygame.sprite.Sprite):
    def __init__(self, owner, max_hp=100, bar_size=(30, 10), border_size=2, bar_color=(255, 0, 0), bg_color_1=(0, 0, 0), bg_color_2=(128, 128, 128)):
        super().__init__(all_sprites)
        self.add(bar_sprites)

        self.owner = owner
        self.max_hp = max_hp
        self.bar_size = bar_size
        self.border_size = border_size
        self.bar_color = bar_color
        self.bg_color_1 = bg_color_1
        self.bg_color_2 = bg_color_2

        self.hp_left = self.max_hp

        self.image = pygame.Surface((self.bar_size[0], self.bar_size[1]), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()

    def update(self):
        if dead_monsters in self.owner.groups():
            self.kill()

        self.hp_left = self.owner.hp_left

        self.rect.x = self.owner.cord_x
        self.rect.y = self.owner.cord_y - self.owner.height

        pygame.draw.rect(self.image, (64, 64, 64), (0, 0, self.bar_size[0], self.bar_size[1]), 0)
        pygame.draw.rect(self.image, (64, 0, 0), (self.border_size, self.border_size, self.bar_size[0] - \
            2 * self.border_size, self.bar_size[1] - 2 * self.border_size), 0)
        pygame.draw.rect(self.image, (255, 64, 64), (self.border_size, self.border_size, (self.bar_size[0] - \
                    2 * self.border_size) * self.hp_left / self.max_hp, self.bar_size[1] - 2 * self.border_size), 0)


def update_hp_bar(bar, health_percent):
    size_delta = (1 - health_percent) * 94
    bar.update_image(image='main_ui.png', image_pos=(214 + size_delta, 0), image_size=(96 - size_delta, 18))

def update_player_balance(sprite):
        sprite.update_text(text=pl.balance)

def update_player_ammo(sprite):
    if pl.active_gun.__class__.__name__ != 'Hands':
        if pl.active_gun.is_reloading_now:
            sprite.update_text(text=f'reloading..')
        else:
            sprite.update_text(text=f'{pl.active_gun.ammo_amount} / {pl.active_gun.ammo}')
    else:
        sprite.update_text(text='0 / 0')

def open_shop():
    shop.set_visible(not shop.is_visible)
    shop.set_page(0)

def flip_shop_page():
    if shop.button_next.mouse_clicked() and shop.current_page + 1 <= len(shop.items_list) // 12:
        shop.flip_page(1)
    
    if shop.button_back.mouse_clicked() and shop.current_page - 1 >= 0:
        shop.flip_page(-1)
    
def buy_item(item):
    if pl.balance >= item.cost:
        pl.balance -= item.cost
        gun = item.content.copy()
        gun.cord_x = pl.cord_x
        gun.cord_y = pl.cord_y


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Game')
    size = width, height = 800, 500  # скорее всего изменится
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    FPS = 60
    running = True

    # Группы
    all_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    gun_sprites = pygame.sprite.Group()
    monster_sprites = pygame.sprite.Group()
    collide_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    bar_sprites = pygame.sprite.Group()
    dead_monsters = pygame.sprite.Group()
    ui_sprites = pygame.sprite.Group()

    # Основные спрайты
    pl = Player((100, 100), '[image_name]')
    gun = Gun(center_pos=(200, 200), image='[image_name]', ammo=999, damage=10, bullet_color=(255, 255, 255), bullet_size=(5, 20), fire_rate=150, shooting_accuracy=0.95)
    gun2 = Gun(center_pos=(300, 200), image='[image_name]', ammo=5, reload_time=1000)
    m1 = Monster((300, 100), '[image_name]')
    m2 = Monster((400, 100), '[image_name]', hp=1)

    # Ui
    player_info = ui.Img(pos=(20, 20), sprite_group=(all_sprites, ui_sprites), image_pos=(56, 0), image_size=(154, 48))
    player_hp_bar = ui.Img(pos=(20 + 54, 20 + 4), image_pos=(214, 0), image_size=(94, 18), sprite_group=(all_sprites, ui_sprites))
    shop_button = ui.Buttons(pos=(720, 20), sprite_group=(all_sprites, ui_sprites), image_pos=(192, 52), image_size=(60, 28))
    player_balance = ui.Text(pos=(90, 50), sprite_group=all_sprites)
    player_ammo = ui.Text(pos=(720, 460), sprite_group=all_sprites)

    # Shop
    shop = ui.Shop(pos=(590, 60), image_pos=(0, 84), image_size=(210, 312), sprite_group=(ui_sprites, all_sprites))

    # Тестовое добавление товаров в магазин
    for _ in range(25):
        gun = Gun(bullet_color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
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
                for sprite in ui_sprites:
                    # Если навелся на UI, то стрелять нельзя
                    if sprite.mouse_hovered():
                        can_shoot = False

                        if shop_button.mouse_clicked():
                            open_shop()
                        
                        # Листать страницы магазина
                        if shop.button_back.mouse_clicked() or shop.button_next.mouse_clicked():
                            flip_shop_page()

                
                # Проверка нажатия на кнопку покупки
                for bg in shop.backgrounds:
                    if bg.mouse_clicked() and shop.is_visible and bg in all_sprites:
                        buy_item(bg.item)
                        
                if can_shoot:
                    pl.on_clicked(event)
            
            if event.type == pygame.KEYDOWN:
                pl.on_k_pressed(event)
            
            if pl.active_gun.__class__.__name__ != 'Hands':
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
                for monster in dead_monsters:
                    monster.respawn()

        pl.move()
        update_hp_bar(player_hp_bar, pl.hp_left / pl.max_hp)
        update_player_balance(player_balance)
        update_player_ammo(player_ammo)

        screen.fill((0, 0, 0))

        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()