import pygame
import os
import random
import math
import time
import ui

mouse_pos = (0, 0)           

class Hands(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)

        self.rect = (0, 0, 0, 0)
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA, 32)

    def try_shoot(self):
        pass


class Player(pygame.sprite.Sprite):
    def __init__(self, center_pos, image):
        super().__init__(all_sprites)
        self.add(player_sprite)

        self.active_gun = Hands()

        self.image = pygame.Surface((50, 50), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, (128, 0, 255), (0, 0, 50, 50), 0)

        self.rect.x = center_pos[0] - self.image.get_width() // 2
        self.rect.y = center_pos[1] - self.image.get_height() // 2

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

        self.balance = 10

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
    def __init__(self, center_pos, image, destroy_bullets=True, damage_type='point', bullet_color=(128, 128, 128), bullet_size=(10, 10), bullet_speed=300, fire_rate=300, \
        damage=0, splash_damage=0, splash_radius=0, ammo=10, reload_time=3000, reload_event=1, shoot_event=2):

        super().__init__(all_sprites)
        self.add(gun_sprites)

        # Их не изменять
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

        self.ammo_amount = self.ammo
        self.reload_time = reload_time

        self.reload_event = pygame.USEREVENT + reload_event
        self.shoot_event = pygame.USEREVENT + shoot_event

        self.image = pygame.Surface((25, 25), pygame.SRCALPHA, 32)
        self.rotate_image = self.image
        self.img_width = self.rotate_image.get_width()
        self.img_height = self.rotate_image.get_height()
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, (128, 255, 128), (0, 0, 25, 25), 0)

        self.rect.x = center_pos[0] - self.img_width / 2
        self.rect.y = center_pos[1] - self.img_height / 2

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

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
                Bullet(pl.active_gun, (self.cord_x, self.cord_y), mouse_pos)
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
        rel_x, rel_y = mouse_pos[0] - self.cord_x - \
            self.img_width / 2, mouse_pos[1] - \
            self.cord_y - self.img_height / 2
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
        rel_x, rel_y = mouse_pos[0] - self.rect.x - \
            self.gun.bullet_size[0] / 2, mouse_pos[1] - \
            self.rect.y - self.gun.bullet_size[1] / 2
        angle = (180 / math.pi) * math.atan2(rel_x, rel_y)
        return angle
    
    def rotate(self):
        self.image = pygame.transform.rotate(self.image, self.math_angle())

    def math_speed(self):
        rel_x, rel_y = (self.cords_to[0] - self.cords_from[0] - \
            self.image.get_width() / \
            2), (self.cords_to[1] - self.cords_from[1] - \
            self.image.get_height() / 2)

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

    
    def update(self):
        self.move()

        self.rect.x = self.cords[0]
        self.rect.y = self.cords[1]

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


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Game')
    size = width, height = 800, 500  # скорее всего изменится
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    FPS = 60
    running = True

    all_sprites = pygame.sprite.Group()
    player_sprite = pygame.sprite.Group()
    gun_sprites = pygame.sprite.Group()
    monster_sprites = pygame.sprite.Group()
    collide_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    bar_sprites = pygame.sprite.Group()
    dead_monsters = pygame.sprite.Group()
    ui_sprites = pygame.sprite.Group()


    pl = Player((100, 100), '[image_name]')
    gun = Gun((200, 200), '[image_name]', ammo=30, damage=10, bullet_color=(255, 255, 255), bullet_size=(5, 20), fire_rate=150)
    gun2 = Gun((300, 200), '[image_name]', ammo=5, reload_time=1000)
    m1 = Monster((300, 100), '[image_name]')
    m2 = Monster((400, 100), '[image_name]', hp=1)
    
    btn1 = ui.Buttons((720, 20), image='main_ui.png', sprite_group=(all_sprites, ui_sprites), image_pos=(192, 52), image_size=(60, 28))

    respawn_monsters = pygame.USEREVENT + 3
    pygame.time.set_timer(respawn_monsters, 3000)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos

            if event.type == pygame.MOUSEBUTTONDOWN:
                can_shoot = True
                for sprite in ui_sprites:

                    if sprite.mouse_clicked():
                        can_shoot = False

                        if btn1.mouse_clicked():
                            print('open the shop')

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

        screen.fill((0, 0, 0))

        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()
