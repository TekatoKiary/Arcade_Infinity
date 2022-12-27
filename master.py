# Это, можно сказать, черновик

import pygame
import os
import random
import math
import time

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

        self.rect.x = center_pos[0] - 50 // 2
        self.rect.y = center_pos[1] - 50 // 2

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

    def update(self):
        self.rect.x = self.cord_x
        self.rect.y = self.cord_y

    def on_clicked(self, event):
        if event.button == 1:
            self.active_gun.try_shoot()
    
    def drop_gun(self):
        pass


class Gun(pygame.sprite.Sprite):
    def __init__(self, center_pos, image, damage_type='point', bullet_color=(128, 128, 128), damage=0, splash_damage=0, splash_radius=0, ammo=10, reload_time=3000, reload_event=1):
        super().__init__(all_sprites)
        self.add(gun_sprites)

        # Их не изменять
        self.bullet_color = bullet_color
        self.damage_type = damage
        self.damage = damage
        self.splash_damage = splash_damage
        self.splash_radius = splash_radius
        self.ammo = ammo

        self.ammo_amount = self.ammo
        self.reload_time = reload_time
        self.reload_event = pygame.USEREVENT + reload_event

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

    def try_shoot(self):
        if not self.is_reloading_now:
            if pl.active_gun.__class__.__name__ != 'Hands':
                if self.ammo_amount > 0:
                    self.shoot()
                else:
                    self.is_reloading_now = True
                    pygame.time.set_timer(self.reload_event, self.reload_time)
    
    def shoot(self):
        self.ammo_amount -= 1
        Bullet(pl.active_gun, (self.cord_x, self.cord_y), mouse_pos)
    
    def reload_ammo(self):
        self.is_reloading_now = False
        self.ammo_amount += self.ammo

    def rotate(self):
        # self.image = pygame.transform.rotate(self.image, int(self.math_angle()))
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

        if pygame.sprite.spritecollide(self, player_sprite, False):
            if pl.active_gun.__class__.__name__ == 'Hands':
                self.is_raised = True

        if self.is_raised:
            pl.active_gun = self
            self.cord_x = pl.cord_x + 30
            self.cord_y = pl.cord_y + 20

            self.rotate()


class Bullet(pygame.sprite.Sprite):
    # damage_type: point, splash
    def __init__(self, gun, cords_from=(0, 0), cords_to=(0, 0), width=10, height=10):
        super().__init__(all_sprites)

        self.gun = gun
        self.cords_from = cords_from
        self.cords_to = cords_to

        self.cords = [self.cords_from[0], self.cords_from[1]]

        self.width = width
        self.height = height
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.x = self.cords_from[0]
        self.rect.y = self.cords_from[1]
        pygame.draw.rect(self.image, self.gun.bullet_color, (0, 0, self.width, self.height), 0)

        self.vx, self.vy = self.math_speed()
        self.rotate()

    def math_angle(self):
        rel_x, rel_y = mouse_pos[0] - self.rect.x - \
            self.width / 2, mouse_pos[1] - \
            self.rect.y - self.height / 2
        angle = (180 / math.pi) * math.atan2(rel_x, rel_y)
        return angle
    
    def rotate(self):
        self.image = pygame.transform.rotate(self.image, self.math_angle())

    def math_speed(self):
        rel_x, rel_y = self.cords_to[0] - self.cords_from[0] - \
            self.image.get_width() / \
            2, self.cords_to[1] - self.cords_from[1] - \
            self.image.get_height() / 2

        vx = round(rel_x / math.sqrt(rel_x ** 2 + rel_y ** 2) * 300, 2)
        vy = round(rel_y / math.sqrt(rel_x ** 2 + rel_y ** 2) * 300, 2)

        return (vx, vy)

    def move(self):
        self.cords[0] += self.vx / 60
        self.cords[1] += self.vy / 60

    def collision_handling(self):
        pass
    
    def update(self):
        self.move()

        self.rect.x = self.cords[0]
        self.rect.y = self.cords[1]

        self.collision_handling()
    


def k_pressed():
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        pl.cord_y -= 80 / 60
    if keys[pygame.K_a]:
        pl.cord_x -= 80 / 60
    if keys[pygame.K_s]:
        pl.cord_y += 80 / 60
    if keys[pygame.K_d]:
        pl.cord_x += 80 / 60


all_sprites = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()
gun_sprites = pygame.sprite.Group()


pl = Player((100, 100), '[image_name]')
gun = Gun((200, 200), '[image_name]', ammo=30)
gun2 = Gun((300, 200), '[image_name]', ammo=5, reload_time=1000)

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Game')
    size = width, height = 800, 500  # скорее всего изменится
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    FPS = 60
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos

            if event.type == pygame.MOUSEBUTTONDOWN:
                pl.on_clicked(event)
            
            if pl.active_gun.__class__.__name__ != 'Hands':
                if event.type == pl.active_gun.reload_event:
                    pl.active_gun.reload_ammo()
                    pygame.time.set_timer(pl.active_gun.reload_event, 0)

        k_pressed()

        screen.fill((0, 0, 0))

        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()
