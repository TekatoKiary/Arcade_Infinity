import pygame
import math
import random
import ui

PLAYER_RELOAD_EVENT = pygame.USEREVENT + 1
PLAYER_SHOOT_EVENT = pygame.USEREVENT + 2

all_sprites = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()
gun_sprites = pygame.sprite.Group()
monster_sprites = pygame.sprite.Group()
collide_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
bar_sprites = pygame.sprite.Group()
dead_monsters = pygame.sprite.Group()
ui_sprites = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, center_pos=(0, 0), image=None, max_hp=100):
        super().__init__(all_sprites)
        self.add(player_sprite)

        self.max_hp = max_hp
        self.hp_left = self.max_hp

        self.inventory_size = 3
        self.inventory = [Gun(player=self, name='first_gun', center_pos=(300, 200), damage=20, ammo=-1, reload_time=1000), \
            *[None for i in range(self.inventory_size - 1)]]
    
        self.active_gun = self.inventory[0]
        self.active_gun.is_raised = True
        self.cells = ui.Inventory(sprite_group=(all_sprites, ui_sprites), player=self)

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

        if event.key == pygame.K_1:
            self.switch_gun(0)
        if event.key == pygame.K_2:
            self.switch_gun(1)
        if event.key == pygame.K_3:
            self.switch_gun(2)


    def take_gun(self):
        if self.inventory.count(None) > 0:
            for gun in gun_sprites:
                if pygame.sprite.spritecollide(gun, player_sprite, False):
                    if gun.can_be_raised and gun not in self.inventory:
                        gun.is_raised = True
                        gun.set_display(False)
                        for i, item in enumerate(self.inventory):
                            if item == None:
                                self.inventory[i] = gun
                                break
                        break
            self.cells.update()
            
    def drop_gun(self):
        if self.inventory.count(None) < 2:
            self.active_gun.is_raised = False
            self.active_gun.is_reloading_now = False
            pygame.time.set_timer(self.active_gun.reload_event, 0)
            self.active_gun.can_shoot = True
            pygame.time.set_timer(self.active_gun.shoot_event, 0)
            
            self.inventory.remove(self.active_gun)
            self.inventory.append(None)
            for item in self.inventory[::-1]:
                if item != None:
                    self.active_gun = item
            self.active_gun.set_display(True)
            self.cells.update()
    
    def switch_gun(self, n):
        if self.inventory[n] != None:
            self.active_gun.is_reloading_now = False
            pygame.time.set_timer(self.active_gun.reload_event, 0)
            self.active_gun.can_shoot = True
            pygame.time.set_timer(self.active_gun.shoot_event, 0)
            self.active_gun.set_display(False)
            self.active_gun = self.inventory[n]
            self.active_gun.set_display(True)
            self.cells.update()

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
    # damage_type: point, splash
    def __init__(self, player, target_group=monster_sprites, name='gun', can_be_raised=True, center_pos=(0, 0), image=None, destroy_bullets=True, damage_type='point', bullet_image=None, bullet_color=(128, 128, 128), \
        bullet_size=(10, 10), bullet_speed=300, fire_rate=300, shooting_accuracy=1, damage=0, splash_damage=10, splash_radius=150, ammo=10, \
            reload_time=3000):

        super().__init__()
        self.add(gun_sprites, all_sprites)

        self.player = player
        self.target_group = target_group
        self.name = name

        # Их не изменять
        self.center_pos = center_pos
        self.destroy_bullets = destroy_bullets
        self.bullet_color = bullet_color
        self.bullet_image = bullet_image
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

        self.reload_event = PLAYER_RELOAD_EVENT
        self.shoot_event = PLAYER_SHOOT_EVENT

        if image == None:
            self.image = pygame.Surface((25, 25), pygame.SRCALPHA, 32)
            pygame.draw.rect(self.image, self.bullet_color, (0, 0, 25, 25), 0)
        else:
            self.image = image

        self.rotate_image = self.image
        self.rect = self.image.get_rect(center = center_pos)

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

        self.can_be_raised = can_be_raised
        self.is_displayed = True
        self.is_raised = False
        self.is_reloading_now = False
        self.can_shoot = True
    
    def set_display(self, bool):
        if bool:
            self.is_displayed = True
            self.add(gun_sprites, all_sprites)
        else:
            self.is_displayed = False
            all_sprites.remove(self)
        

    def try_shoot(self):
        if self.can_shoot:
            self.shoot(target_pos=pygame.mouse.get_pos())
            self.can_shoot = False
            pygame.time.set_timer(self.shoot_event, self.fire_rate)
    
    def shoot(self, target_pos):
        if not self.is_reloading_now:
            if self.ammo_amount != 0:
                self.ammo_amount -= 1
                Bullet(self, (self.cord_x, self.cord_y), target_pos)
            else:
                self.is_reloading_now = True
                pygame.time.set_timer(self.reload_event, self.reload_time)
    
    def reload_ammo(self):
        self.is_reloading_now = False
        self.ammo_amount += self.ammo

    def rotate(self, target):
        self.image = pygame.transform.rotate(
            self.rotate_image, self.math_angle(target))

    def math_angle(self, target):
        rel_x, rel_y = target[0] - self.cord_x - \
            self.rotate_image.get_width() / 2, target[1] - \
            self.cord_y - self.rotate_image.get_height() / 2
        angle = (180 / math.pi) * math.atan2(rel_x, rel_y)
        return angle
    
    def copy(self):
        return Gun(player=self.player, target_group=monster_sprites, can_be_raised=self.can_be_raised, name=self.name, center_pos=self.center_pos, image=self.image, destroy_bullets=self.destroy_bullets, \
            damage_type=self.damage_type, bullet_image=None, bullet_color=self.bullet_color, bullet_size=self.bullet_size, bullet_speed=self.bullet_speed, \
                fire_rate=self.fire_rate, shooting_accuracy=self.shooting_accuracy, damage=self.damage, splash_damage=self.splash_damage, \
                    splash_radius=self.splash_radius, ammo=self.ammo, reload_time=self.reload_time)

    def update(self):
        self.rect.x = self.cord_x
        self.rect.y = self.cord_y

        if self.is_raised:
            self.cord_x = self.player.cord_x + 30
            self.cord_y = self.player.cord_y + 20

            self.rotate(target=pygame.mouse.get_pos())


class Bullet(pygame.sprite.Sprite):
    def __init__(self, gun, cords_from=(0, 0), cords_to=(0, 0)):
        super().__init__(all_sprites)
        self.add(bullet_group)

        self.gun = gun
        self.target_group = self.gun.target_group
        self.cords_from = cords_from
        self.cords_to = cords_to

        self.cords = [self.cords_from[0], self.cords_from[1]]
        
        if self.gun.bullet_image == None:
            self.image = pygame.Surface((self.gun.bullet_size[0], self.gun.bullet_size[1]), pygame.SRCALPHA, 32)
            pygame.draw.rect(self.image, self.gun.bullet_color, (0, 0, self.gun.bullet_size[0], self.gun.bullet_size[1]), 0)
        else:
            self.image = self.gun.bullet_image
        self.rect = self.image.get_rect()
        self.rect.x = self.cords_from[0]
        self.rect.y = self.cords_from[1]

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
        sprite_collided = pygame.sprite.spritecollide(self, self.target_group, False)
        if sprite_collided:
            sprite_collided = sprite_collided[0]
            if self.gun.destroy_bullets:
                self.kill()

            sprite_collided.hp_left -= self.gun.damage

            if self.gun.damage_type == 'splash':
                self.splash_damage(sprite_collided)
    
    def splash_damage(self, sprite):
        splash = pygame.sprite.Sprite()
        splash.image = pygame.Surface((self.gun.splash_radius, self.gun.splash_radius), pygame.SRCALPHA, 32)
        splash.rect = splash.image.get_rect(center = (self.rect.centerx, self.rect.centery))
        for target in self.gun.target_group:
            if target != sprite:
                if (self.rect.centerx - target.rect.centerx) ** 2 + (self.rect.centery - target.rect.centery) ** 2 < self.gun.splash_radius ** 2:
                    target.hp_left -= self.gun.splash_damage
        
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
    def __init__(self, player, center_pos, image, hp=100, reward=1, attack_range=200, gun=None, dead=False, running_speed=50, player_avoidance=True, move_randomly=True):
        super().__init__(all_sprites)
        self.player = player
        self.add(monster_sprites)
        self.add(collide_group)

        if gun == None:
            self.active_gun = Gun(player=self.player, name='bad pistol', damage=5, can_be_raised=False, bullet_color=(random.randint(96, 196), random.randint(96, 196), random.randint(96, 196)), fire_rate=1000, ammo=-1, shooting_accuracy=0.9, target_group=player_sprite)
        else:
            self.active_gun = gun

        self.player_avoidance = player_avoidance
        self.attack_range = attack_range
        self.running_speed = running_speed
        self.max_hp = hp
        self.reward = reward
        self.hp_left = self.max_hp

        self.hp_bar = Bars(owner=self, max_hp=self.max_hp)

        self.image = image
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * 3, self.image.get_height() * 3))
        self.rect = self.image.get_rect(center = center_pos)

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

        self.shooting_timer = random.randint(0, 30)
        self.movement_timer = 20
        self.movement_direction = 1
        self.move_randomly = move_randomly


        if dead:
            self.die()
    
    def respawn(self):
        self.hp_left = self.max_hp
        self.add(all_sprites, collide_group, monster_sprites)
        dead_monsters.remove(self)
        self.hp_bar.add(all_sprites, bar_sprites)
        self.active_gun.add(all_sprites, gun_sprites)
    
    def die(self):
        self.hp_left = 0
        self.kill()
        self.add(dead_monsters)
    
    def give_reward(self):
        self.player.give_money(self.reward)
    
    def shoot(self):
        if self.shooting_timer > 0:
            if random.randint(0, 4) == 0:
                self.shooting_timer -= 1
        else:
            self.active_gun.shoot((self.player.rect.centerx, self.player.rect.centery))
            self.shooting_timer = 10
    
    def walk(self, movement_direction=1, random_direction=(1, 1)):
        distance = max(math.sqrt((self.rect.centerx - self.player.rect.centerx) ** 2 + (self.rect.centery - self.player.rect.centery) ** 2), 1)
        vx = (self.rect.centerx - self.player.rect.centerx) / distance / 60 * self.running_speed
        vy = (self.rect.centery - self.player.rect.centery) / distance / 60 * self.running_speed

        self.cord_x -= movement_direction * vx * random_direction[0]
        self.cord_y -= movement_direction * vy * random_direction[1]
        
    def run_away(self):
        if self.player_avoidance:
            if self.current_distance_sqr < self.attack_range ** 2 / 3:
                self.walk(movement_direction=-1)

    
    def distance_check(self):
        self.current_distance_sqr = (self.rect.centerx - self.player.rect.centerx) ** 2 + (self.rect.centery - self.player.rect.centery) ** 2
        if self.current_distance_sqr < (self.attack_range + 100) ** 2:
            self.shoot()

        if self.current_distance_sqr < self.attack_range ** 2:
            self.run_away()
        else:
            self.walk()
            
        self.random_movement()
    
    def random_movement(self):
        if self.move_randomly:
            if self.movement_timer > 0:
                if random.randint(0, 15) == 0:
                    self.movement_timer -= 1
            else:
                self.movement_direction = self.movement_direction * -1
                self.movement_timer = 10
            self.walk(random_direction=(self.movement_direction / 2, self.movement_direction / 2))

    def update(self):
        if self.hp_left <= 0:
            self.die()
            self.give_reward()
            self.active_gun.kill()
        else:
            self.rect.x = self.cord_x
            self.rect.y = self.cord_y

            self.active_gun.cord_x = self.rect.centerx
            self.active_gun.cord_y = self.rect.centery

            self.distance_check()
            self.active_gun.rotate(self.player.rect.center)


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

        self.rect.x = self.owner.rect.centerx - self.bar_size[0] / 2
        self.rect.y = self.owner.cord_y - 20

        pygame.draw.rect(self.image, (64, 64, 64), (0, 0, self.bar_size[0], self.bar_size[1]), 0)
        pygame.draw.rect(self.image, (64, 0, 0), (self.border_size, self.border_size, self.bar_size[0] - \
            2 * self.border_size, self.bar_size[1] - 2 * self.border_size), 0)
        pygame.draw.rect(self.image, (255, 64, 64), (self.border_size, self.border_size, (self.bar_size[0] - \
                    2 * self.border_size) * self.hp_left / self.max_hp, self.bar_size[1] - 2 * self.border_size), 0)