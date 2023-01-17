import math
import ui
import random
import pygame
import others
from others import is_collide_with_speed, TILED_MAP_DIR
import pytmx
import images
from images import GUN_TEXTURES

# В чем смысл id: в tiled комнаты есть отдельный слой, где как раз хранятся особенные плитки - флажки.
# Так как это плитка, следовательно, у неё есть id.
# Какие есть id и что они означают: об id написано в классах, где используют их


PLAYER_RELOAD_EVENT = pygame.USEREVENT + 1
PLAYER_SHOOT_EVENT = pygame.USEREVENT + 2

# В принципе, если перевести название, то сразу станет понятно, что за группы спрайтов
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.GroupSingle()
gun_sprites = pygame.sprite.Group()
monster_sprites = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
bar_sprites = pygame.sprite.Group()
ui_sprites = pygame.sprite.Group()
torch_group = pygame.sprite.Group()
heal_group = pygame.sprite.Group()
cell_group = pygame.sprite.Group()
barrel_group = pygame.sprite.Group()
dead_group = pygame.sprite.Group()

spike_damage_delay = 1  # Переменная нужна для класса Spike. Там будет объяснение значения переменной


class Player(pygame.sprite.Sprite):
    """Класс Player. Создается игрок"""  # Я больше ничего не мог придумать, чтобы объяснить, что такое Player

    def __init__(self, max_hp=100):
        super().__init__()
        self.add(player_group)
        self.image = images.player_image
        self.max_hp = max_hp
        self.hp_left = self.max_hp
        self.current_level = 1

        self.inventory_size = 3
        self.inventory = []

        self.images_stand = images.player_images_stand
        self.images_move = images.player_images_move
        self.rect = self.image.get_rect()
        self.rect.x = others.WIDTH // 2
        self.rect.y = others.HEIGHT // 2
        image = pygame.transform.scale(self.image,
                                       (30, self.image.get_rect().height - self.rect.height // 1.01))
        self.mask = pygame.mask.from_surface(image)  # маска нужна для коллизии с бочками
        # Зачем нужен новый image с изменёнными параметрами: в маске будет храниться изображение, можно сказать, ног
        self.cnt = 0  # счетчик для анимации спрайтов
        self.step = 10  # именно настолько увеличивается self.cnt
        self.is_moving = False  # он идет или нет? Вот в чем вопрос
        self.left_right = 1  # взгляд направо - 1, взгляд налево - 0
        self.is_attacking = False

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

        self.balance = 0

    def set_inventory(self, inventory):
        """Метод класса. Установка инвентаря игрока"""
        [i.kill() for i in self.inventory if i]
        self.inventory = inventory
        for i in self.inventory:
            if i:
                i.player = self
                i.is_raised = True
        self.active_gun = self.inventory[0]
        self.cells = ui.Inventory(sprite_group=(all_sprites, ui_sprites), player=self)

    def draw(self, screen):
        """Метод класса. Отрисовка игрока"""
        if self.is_moving:  # отрисовка движения
            screen.blit(self.images_move[self.cnt // self.step], self.rect)
        elif self.is_attacking:  # отрисовка атаки
            screen.blit(self.images_stand[0], self.rect)
        else:  # отрисовка статичного игрока
            screen.blit(self.images_stand[self.cnt // self.step], self.rect)
        self.active_gun.draw(screen)

    def move(self, x, y):
        """Метод класса. Движение игрока"""
        self.rect.x = others.WIDTH // 2 - self.rect.width // 2  # он всегда остаётся в центре(внимания) экрана
        self.rect.y = others.HEIGHT // 2 - self.rect.height // 2
        if (x or y) and not self.is_moving:  # если он начинает движение, но до этого стоял
            self.cnt = 0
            self.is_moving = True
        elif (x or y) and self.is_moving:  # если он двигается
            self.cnt += -self.cnt if self.cnt >= self.step * (len(self.images_move) - 1) else 1
        elif not (x or y) and self.is_moving:  # если он начинает стоять, но до этого двигался
            self.is_moving = False
            self.cnt = 0
        elif not (x or y) and not self.is_moving:  # если он стоит
            self.cnt += -self.cnt if self.cnt >= self.step * (len(self.images_stand) - 1) else 1
        self._set_left_right()

    def _set_left_right(self):
        """Метод класса. Определяет взгляд игрока относительно мышки пользователя"""
        # решил сделать так: мышка на левой стороне экрана игры - персонаж смотрит налево и даже когда идет направо;
        # мышка на правой стороне экрана игры - персонаж смотрит направо и даже когда идет налево
        # Лучше будет, если персонаж идет назад и стреляет впереди себя, а не идет прямо и стреляет куда-то позади себя
        x, y = pygame.mouse.get_pos()
        if x >= others.WIDTH // 2 and not self.left_right:
            self.left_right = 1
            self.images_move = [pygame.transform.flip(i, True, False) for i in self.images_move]
            self.images_stand = [pygame.transform.flip(i, True, False) for i in self.images_stand]
        elif x < others.WIDTH // 2 and self.left_right:
            self.left_right = 0
            self.images_move = [pygame.transform.flip(i, True, False) for i in self.images_move]
            self.images_stand = [pygame.transform.flip(i, True, False) for i in self.images_stand]

    def take_damage(self, damage):
        """Метод класса. Уменьшение здоровья игрока полученным уроном"""
        self.hp_left -= damage

    def on_clicked(self, event):
        """Метод класса. Проверка нажатия мыши"""
        if event.button == 1:
            damage = self.active_gun.damage
            if self.current_level >= 20:
                self.active_gun.damage *= 0.5
            elif self.current_level >= 10:
                self.active_gun.damage *= 0.75
            self.active_gun.try_shoot()
            self.is_attacking = True
            self.active_gun.damage = damage
        else:
            self.is_attacking = False

    def on_k_pressed(self, event):
        """Метод класса. Проверка нажатия клавиш"""
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
        """Метод класса. Если у игрока свободен хотя бы один слот инвентаря, то он подбирает оружие"""
        if self.inventory.count(None) > 0:
            for gun in gun_sprites:
                if pygame.sprite.spritecollide(gun, player_group, False):
                    if gun.can_be_raised and gun not in self.inventory and not gun.is_raised:
                        gun.player = self
                        gun.is_raised = True
                        gun.set_display(False)
                        gun_sprites.remove(gun)
                        for i, item in enumerate(self.inventory):
                            if item is None:
                                self.inventory[i] = gun
                                break
                        break
            self.cells.update()

    def drop_gun(self):
        """Метод класса. Игрок выбрасывает текущее оружие, если это не последнее оружие"""
        if self.inventory.count(None) < 2:
            self.active_gun.is_raised = False
            gun_sprites.add(self.active_gun)
            self.active_gun.is_reloading_now = False
            pygame.time.set_timer(self.active_gun.reload_event, 0)
            self.active_gun.can_shoot = True
            pygame.time.set_timer(self.active_gun.shoot_event, 0)

            self.inventory.remove(self.active_gun)
            self.inventory.append(None)
            for item in self.inventory[::-1]:
                if item is not None:
                    self.active_gun = item
            self.active_gun.set_display(True)
            self.cells.update()

    def switch_gun(self, n):
        """Метод класса. Игрок меняет оружие, которые находятся в инвентаре"""
        if self.inventory[n]:
            self.active_gun.is_reloading_now = False
            pygame.time.set_timer(self.active_gun.reload_event, 0)
            self.active_gun.can_shoot = True
            pygame.time.set_timer(self.active_gun.shoot_event, 0)
            self.active_gun.set_display(False)
            self.active_gun = self.inventory[n]
            self.active_gun.set_display(True)
            self.cells.update()

    def give_money(self, reward):
        """Метод класса. Игрок получает определенное кол-во монет"""
        self.balance += reward

    def update(self):
        """Метод класса. Обновление игрока"""
        self.rect.x = self.cord_x
        self.rect.y = self.cord_y
        self.active_gun.update()

    def set_current_level(self, current_level):
        self.current_level = current_level


class Gun(pygame.sprite.Sprite):
    """Класс Gun. Создается оружие"""

    # damage_type: point, splash
    def __init__(self, player=None, target_group=monster_sprites, name='gun', can_be_raised=True, center_pos=(0, 0),
                 image=None, destroy_bullets=True, damage_type='point', bullet_image=None, bullet_color=(128, 128, 128),
                 bullet_size=(10, 10), bullet_speed=300, fire_rate=300, shooting_accuracy=1, damage=0, splash_damage=10,
                 splash_radius=200, ammo=10, reload_time=3000):

        super().__init__()
        self.add(gun_sprites)

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

        self.original_image = image
        if image is None:
            self.image = pygame.Surface((25, 25), pygame.SRCALPHA, 32)
            pygame.draw.rect(self.image, self.bullet_color, (0, 0, 25, 25), 0)
        else:
            self.image = pygame.transform.scale(image, (image.get_width() * 1.5, image.get_height() * 1.5))

        self.rotate_image = self.image
        self.rect = self.image.get_rect(center=center_pos)

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

        self.can_be_raised = can_be_raised
        self.is_displayed = True
        self.is_raised = False
        self.is_reloading_now = False
        self.can_shoot = True
        self.left_right = 1  # взгляд направо - 1, взгляд налево - 0

    def draw(self, screen):
        """Метод класса. Отрисовка оружия"""
        if self.is_raised and self.player.active_gun != self:  # если он в инвентаре и он не текущее оружие игрока то...
            return
        screen.blit(self.image, self.rect)

    def set_display(self, flag):
        if flag:
            self.is_displayed = True
            if self not in gun_sprites:
                self.add(gun_sprites)
        else:
            self.is_displayed = False

    def try_shoot(self):
        if self.can_shoot:
            self.shoot(target_pos=pygame.mouse.get_pos())
            self.can_shoot = False
            pygame.time.set_timer(self.shoot_event, self.fire_rate)

    def shoot(self, target_pos):
        """Метод класса. Производится подобие выстрела, то есть просто создается пуля"""
        if not self.is_reloading_now:
            if self.ammo_amount > 0 or self.ammo < 0:
                self.ammo_amount -= 1
                Bullet(self, target_pos)
            if self.ammo_amount <= 0 and self.ammo > 0:
                self.is_reloading_now = True
                pygame.time.set_timer(self.reload_event, self.reload_time)

    def reload_ammo(self):
        """Метод класса. Перезарядка оружия"""
        self.is_reloading_now = False
        self.ammo_amount = self.ammo

    def rotate(self, target):
        """Метод класса. Вращение оружия"""
        self.image = pygame.transform.rotate(
            self.rotate_image, self.math_angle(target) - 90)

    def math_angle(self, target):
        rel_x, rel_y = target[0] - self.cord_x - \
                       self.rotate_image.get_width() / 2, target[1] - \
                       self.cord_y - self.rotate_image.get_height() / 2
        angle = (180 / math.pi) * math.atan2(rel_x, rel_y)
        return angle

    def copy(self, center_pos=None):
        """Метод класса. Возвращает копию этого оружия"""
        if center_pos is None:
            center_pos = self.center_pos
        return Gun(player=None, target_group=monster_sprites, can_be_raised=self.can_be_raised, name=self.name,
                   center_pos=center_pos, image=self.original_image, destroy_bullets=self.destroy_bullets,
                   damage_type=self.damage_type, bullet_image=self.bullet_image, bullet_color=self.bullet_color,
                   bullet_size=self.bullet_size, bullet_speed=self.bullet_speed, fire_rate=self.fire_rate,
                   shooting_accuracy=self.shooting_accuracy, damage=self.damage, splash_damage=self.splash_damage,
                   splash_radius=self.splash_radius, ammo=self.ammo, reload_time=self.reload_time)

    def update(self):
        """Метод класса. Обновление оружия"""
        self.rect.x = self.cord_x
        self.rect.y = self.cord_y

        if self.is_raised:
            if self.left_right != self.player.left_right and self == self.player.active_gun:
                self.left_right = self.player.left_right
                self.rotate_image = pygame.transform.flip(self.rotate_image, False, True)
            self.cord_x = self.player.cord_x - self.rect.width // 2 + (5 if self.left_right else -5)
            self.cord_y = self.player.cord_y - self.rect.height // 2 + 4

            if type(self.player) == Player:
                self.rotate(target=pygame.mouse.get_pos())

    def move(self, x, y):
        """Метод класса. Движение оружия"""
        if not self.is_raised:
            self.cord_x -= x
            self.cord_y -= y


class Shotgun(Gun):
    def __init__(self, player=None, is_raised=False, target_group=monster_sprites, name='gun',
                 can_be_raised=True, center_pos=(0, 0), image=None, destroy_bullets=True, damage_type='point',
                 bullet_image=None, bullet_color=(128, 128, 128), bullet_size=(10, 10), bullet_speed=300,
                 fire_rate=300, shooting_accuracy=1, damage=0, splash_damage=10, splash_radius=150, ammo=10,
                 reload_time=3000):
        super().__init__(is_raised, target_group, name, can_be_raised, center_pos, image, destroy_bullets,
                         damage_type, bullet_image, bullet_color, bullet_size, bullet_speed, fire_rate,
                         shooting_accuracy, damage, splash_damage, splash_radius, ammo, reload_time)

    def shoot(self, target_pos):
        if not self.is_reloading_now:
            if self.ammo_amount > 0:
                self.ammo_amount -= 1
                for _ in range(5):
                    self.bullet_speed = random.randint(250, 350)
                    Bullet(self, target_pos)
            else:
                self.is_reloading_now = True
                pygame.time.set_timer(self.reload_event, self.reload_time)

    def copy(self, center_pos=None):
        """Метод класса. Возвращает копию этого оружия"""
        if center_pos is None:
            center_pos = self.center_pos
        return Shotgun(player=player_group.sprite, target_group=monster_sprites, can_be_raised=self.can_be_raised,
                       name=self.name, center_pos=center_pos, image=self.original_image, reload_time=self.reload_time,
                       destroy_bullets=self.destroy_bullets, damage_type=self.damage_type, ammo=self.ammo,
                       bullet_image=self.bullet_image, bullet_color=self.bullet_color, splash_radius=self.splash_radius,
                       bullet_size=self.bullet_size, bullet_speed=self.bullet_speed, fire_rate=self.fire_rate,
                       shooting_accuracy=self.shooting_accuracy, damage=self.damage, splash_damage=self.splash_damage)


class Bullet(pygame.sprite.Sprite):
    """Класс Gun. Создается пуля"""

    def __init__(self, gun, cords_to=(0, 0)):
        super().__init__()
        self.add(bullet_group)

        self.gun = gun
        self.target_group = self.gun.target_group
        self.cords_to = cords_to
        self.cords_from = (self.gun.rect.centerx, self.gun.rect.centery)

        self.cords = [self.cords_from[0], self.cords_from[1]]
        self.damage = gun.damage
        self.splashdamage = gun.splash_damage

        if self.gun.bullet_image is None:
            self.image = pygame.Surface((self.gun.bullet_size[0], self.gun.bullet_size[1]), pygame.SRCALPHA, 32)
            pygame.draw.rect(self.image, self.gun.bullet_color,
                             (0, 0, self.gun.bullet_size[0], self.gun.bullet_size[1]), 0)
        else:
            self.image = self.gun.bullet_image
        self.rect = self.image.get_rect()
        self.rect.x = self.cords_from[0]
        self.rect.y = self.cords_from[1]
        self.mask = pygame.mask.from_surface(self.image)
        self.vx, self.vy = self.math_speed()
        self.rotate()

    def math_angle(self):
        rel_x, rel_y = self.randomized_mouse_cord_x - self.rect.x - \
                       self.gun.bullet_size[0] / 2, self.randomized_mouse_cord_y - \
                       self.rect.y - self.gun.bullet_size[1] / 2
        angle = (180 / math.pi) * math.atan2(rel_x, rel_y)
        return angle

    def rotate(self):
        """Метод класса. Вращение пули"""
        self.image = pygame.transform.rotate(self.image, self.math_angle())

    def math_speed(self):
        """Метод класса. Возвращает скорость пули"""
        self.randomized_mouse_cord_x = self.cords_to[0] + random.choice([-1, 1]) * random.uniform(0, (
                1 - self.gun.shooting_accuracy)) * self.cords_to[0]

        self.randomized_mouse_cord_y = self.cords_to[1] + random.choice([-1, 1]) * random.uniform(0, (
                1 - self.gun.shooting_accuracy)) * self.cords_to[1]

        rel_x = self.randomized_mouse_cord_x - self.cords_from[0] - self.image.get_width() / 2
        rel_y = self.randomized_mouse_cord_y - self.cords_from[1] - self.image.get_height() / 2

        vx = round(rel_x / math.sqrt(rel_x ** 2 + rel_y ** 2) * self.gun.bullet_speed, 2)
        vy = round(rel_y / math.sqrt(rel_x ** 2 + rel_y ** 2) * self.gun.bullet_speed, 2)
        return vx, vy

    def move_trak(self):
        """Метод класса. Собственное движение пули"""
        self.cords[0] += self.vx / 20
        self.cords[1] += self.vy / 20

    def collision_handling(self, is_stay_gates):
        """Метод класса. Проверка коллизии пули с персонажами"""
        sprite_collided = pygame.sprite.spritecollide(self, self.target_group, False)
        if sprite_collided:
            sprite_collided = sprite_collided[0]
            if self.gun.destroy_bullets:
                self.kill()
            if is_stay_gates:
                sprite_collided.hp_left -= self.damage

            if self.gun.damage_type == 'splash':
                self.splash_damage(sprite_collided)

    def splash_damage(self, sprite):
        """Метод класса.
        Пуля наносит не только персонажу, в которого она попала, но и другим, кто я рядом с этим персонажем"""
        splash = pygame.sprite.Sprite()
        splash.image = pygame.Surface((self.gun.splash_radius, self.gun.splash_radius), pygame.SRCALPHA, 32)
        splash.rect = splash.image.get_rect(center=(self.rect.centerx, self.rect.centery))
        for target in self.gun.target_group:
            if target != sprite:
                if (self.rect.centerx - target.rect.centerx) ** 2 + (
                        self.rect.centery - target.rect.centery) ** 2 < self.gun.splash_radius ** 2:
                    target.hp_left -= self.splashdamage

    def update(self, is_stay_gates):
        """Метод класса. Обновление пули"""
        self.move_trak()

        self.rect.x = self.cords[0]
        self.rect.y = self.cords[1]

        self.collision_handling(is_stay_gates)

    def move(self, x, y):
        """Метод класса. Движение пули"""
        self.cords[0] -= x
        self.cords[1] -= y


class Monster(pygame.sprite.Sprite):
    """Класс-родитель для класса Ghoul и Zombie. Создается монстр"""

    def __init__(self, player, center_pos, hp=100, reward=1, attack_range=200, gun=None, running_speed=50,
                 player_avoidance=True, move_randomly=True, current_level=1):
        super().__init__()
        self.player = player
        self.add(monster_sprites)

        self.active_gun = gun

        self.player_avoidance = player_avoidance
        self.attack_range = attack_range
        self.running_speed = running_speed
        self.max_hp = hp
        self.current_level = current_level
        self.reward = reward // (2 if current_level >= 10 else 1)
        self.hp_left = self.max_hp

        self.hp_bar = Bars(owner=self, max_hp=self.max_hp)

        self.rect = self.image.get_rect()
        self.rect.x = self.x = center_pos[0]
        self.rect.y = self.y = center_pos[1]
        image = pygame.transform.scale(self.image,
                                       (self.image.get_rect().width * 2,
                                        self.image.get_rect().height - self.rect.height // 1.01))
        self.mask = pygame.mask.from_surface(image)  # маска нужна для коллизии с бочками
        # Зачем нужен новый image с изменёнными параметрами: в маске будет храниться изображение, можно сказать, ног
        self.random_x = 0  # скорость гуля, которая он выберет случайно
        self.random_y = 0
        self.delay = random.randrange(1, 11) * 10  # задержка между ходьбой
        self.is_moving = 0  # если он двигается

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

        self.shooting_timer = random.randint(0, 30)
        self.movement_timer = 20
        self.movement_direction = 1
        self.move_randomly = move_randomly
        self.cnt_attacking = 60

        self.move_x = 0
        self.move_y = 0

        self.cnt = 0  # счетчик для изменения спрайтов
        self.step = 10  # именно настолько увеличивается self.cnt
        self.is_moving_bool = False  # он идет или нет? Вот в чем вопрос
        self.left_right = 1  # взгляд направо - 1, взгляд налево - 0

    def die(self):
        """Метод класса. Удаление монстра"""
        self.hp_left = 0
        DeadPerson(self.rect.x, self.rect.y, 'Ghoul' if type(self) == Ghoul else 'Zombie')
        self.active_gun.kill()
        self.hp_bar.kill()
        self.kill()

    def give_reward(self):
        """Метод класса. Монстр отдает награду за свою голову игроку"""
        reward = random.randrange(self.reward - 4, self.reward + 5)
        self.player.give_money(reward)

    def shoot(self):
        """Метод класса. Атака монстра"""
        if self.shooting_timer >= 0:
            if random.randint(0, 4) == 0:
                self.shooting_timer -= 1
        else:
            self.active_gun.shoot((self.player.rect.centerx, self.player.rect.centery))
            if type(self) == Ghoul:
                self.player.take_damage(self.active_gun.damage)
            self.shooting_timer = 10 if type(self) == Ghoul else 20
            self.cnt_attacking = 0

    def walk(self, movement_direction=1, random_direction=1):
        """Метод класса. Устанавливается скорость монстра"""
        distance = max(math.sqrt(
            (self.rect.centerx - self.player.rect.centerx) ** 2 + (self.rect.centery - self.player.rect.centery) ** 2),
            1)
        vx = (self.rect.centerx - self.player.rect.centerx) / distance / 30 * self.running_speed
        vy = (self.rect.centery - self.player.rect.centery) / distance / 30 * self.running_speed
        self.move_x = int(-movement_direction * vx * random_direction) + self.random_x
        self.move_y = int(-movement_direction * vy * random_direction) + self.random_y

    def run_away(self):
        if self.player_avoidance:
            if self.current_distance_sqr < self.attack_range ** 2 / 3:
                self.walk(movement_direction=-1)

    def distance_check(self):
        """Метод класса. Проверка дистанции от монстра до игрока"""
        self.current_distance_sqr = (self.rect.centerx - self.player.rect.centerx) ** 2 + (
                self.rect.centery - self.player.rect.centery) ** 2
        if self.current_distance_sqr < (self.attack_range + 100) ** 2:
            self.shoot()

        if self.current_distance_sqr < self.attack_range ** 2:
            self.run_away()
        else:
            self.walk()

        self.random_movement()

    def random_movement(self):
        """Метод класса. Устанавливается случайная скорость монстра. В основном для зомби"""
        if self.move_randomly:
            if self.movement_timer > 0:
                if random.randint(0, 15) == 0:
                    self.movement_timer -= 1
            else:
                self.movement_direction = self.movement_direction * -1
                self.movement_timer = 10
            self.walk(random_direction=self.movement_direction / 2)

    def update(self):
        """Метод класса. Обновление монстра"""
        if self.hp_left <= 0:  # смерть монстра
            self.give_reward()
            self.die()
        else:
            self.rect.x = self.cord_x
            self.rect.y = self.cord_y

            self.active_gun.cord_x = self.rect.centerx
            self.active_gun.cord_y = self.rect.centery

            self.distance_check()
            self.active_gun.rotate(self.player.rect.center)

    def draw(self, screen):
        """Метод класса. Отрисовка монстра"""
        if type(self) == Ghoul and self.cnt_attacking != 60:
            screen.blit(self.images_attack[self.cnt_attacking // 10], self.rect)
            self.cnt_attacking += 1
        elif self.is_moving_bool:
            screen.blit(self.images_move[self.cnt // self.step], self.rect)
        else:
            screen.blit(self.images_stand[self.cnt // self.step], self.rect)
        self.active_gun.draw(screen)

    def move(self, x, y):
        """Метод класса. Движение монстра относительно игрока"""
        self.rect.x -= x
        self.cord_x = self.rect.x
        self.rect.y -= y
        self.cord_y = self.rect.y

    def set_left_right(self):
        """Метод класса. Определяет взгляд игрока относительно расположение пользователя"""
        # решил сделать так: мышка на левой стороне экрана игры - персонаж смотрит налево и даже когда идет направо;
        # мышка на правой стороне экрана игры - персонаж смотрит направо и даже когда идет налево
        # Лучше будет, если персонаж идет назад и стреляет впереди себя, а не идет прямо и стреляет куда-то позади себя
        if self.rect.x < others.WIDTH // 2 and not self.left_right:
            self.left_right = 1
            self.images_move = [pygame.transform.flip(i, True, False) for i in self.images_move]
            self.images_stand = [pygame.transform.flip(i, True, False) for i in self.images_stand]
            if type(self) == Ghoul:
                self.images_attack = [pygame.transform.flip(i, True, False) for i in self.images_attack]
        elif self.rect.x > others.WIDTH // 2 and self.left_right:
            self.left_right = 0
            self.images_move = [pygame.transform.flip(i, True, False) for i in self.images_move]
            self.images_stand = [pygame.transform.flip(i, True, False) for i in self.images_stand]
            if type(self) == Ghoul:
                self.images_attack = [pygame.transform.flip(i, True, False) for i in self.images_attack]

    def self_move(self):
        """Метод класса. Движение монстра вне зависимости игрока"""
        self.rect.x += self.move_x
        self.cord_x = self.rect.x
        self.rect.y += self.move_y
        self.cord_y = self.rect.y
        x = self.move_x
        y = self.move_y
        if (x or y) and not self.is_moving_bool:  # если он начинает движение, но до этого стоял
            self.cnt = 0
            self.is_moving_bool = True
        elif (x or y) and self.is_moving_bool:  # если он двигается
            self.cnt += -self.cnt if self.cnt >= self.step * (len(self.images_move) - 1) else 1
        elif not (x or y) and self.is_moving_bool:  # если он начинает стоять, но до этого двигался
            self.is_moving_bool = False
            self.cnt = 0
        elif not (x or y) and not self.is_moving_bool:  # если он стоит
            self.cnt += -self.cnt if self.cnt >= self.step * (len(self.images_stand) - 1) else 1
        self.set_left_right()

    def collide_with_wall(self, x, y, map_surface, layer, tile_size):
        """Метод класса. Коллизия между монстром и непроходимой стеной"""
        x = (self.rect.x + self.move_x - x + (self.rect.width if self.move_x >= 0 else 0)) // tile_size
        y = int(self.rect.y + self.rect.height // 1.01 + self.move_y - y + (
            (self.rect.height - self.rect.height // 1.1) if self.move_y >= 0 else 0)) // tile_size
        # x и y - координаты относительно tiled комнаты.
        # Так как комнаты сделано в tiled editor map, следовательно, комнаты плиточные.
        # Тогда х и у - координаты плитки, на которой стоит монстр
        if -1 < x < map_surface.width and -1 < y < map_surface.height:
            image = map_surface.get_tile_image(x, y, layer)
            if image:
                self.move_x = 0
                self.move_y = 0


class Ghoul(Monster):
    """Класс Ghoul. Создается гуль"""

    def __init__(self, player, center_pos, hp=75, reward=1, attack_range=200, running_speed=50, player_avoidance=True,
                 move_randomly=True, current_level=1):
        self.image = images.ghoul_image
        self.images_stand = images.ghoul_images_stand
        self.images_move = images.ghoul_images_move
        self.images_attack = images.ghoul_images_attack
        gun = GUNS['Fists'].copy()
        gun.target_group = player_group
        gun.player = self
        gun.can_be_raised = False
        gun.fire_rate *= 2 if current_level < 15 else 1
        hp *= 2 if current_level >= 15 else 1
        if current_level >= 20:
            gun.damage = int(2 * self.active_gun.damage)
        elif current_level >= 10:
            gun.damage = int(1.5 * self.active_gun.damage)
        super(Ghoul, self).__init__(player, center_pos, hp, reward, attack_range, gun, running_speed, player_avoidance,
                                    move_randomly, current_level)

    def self_move(self):
        """Метод класса. Движение монстра вне зависимости игрока"""
        # Создается случайная скорость гуля. Нужно, чтобы игроку жизнь медом не казалась
        if self.delay - 1 == 0 and self.is_moving == 0:  # если задержка закончилась и он не двигается
            self.is_moving = random.randrange(1, 21)
            self.delay = 0
            self.random_x = random.randrange(-5, 6)
            self.random_y = random.randrange(-5, 6)
        elif self.delay == 0 and self.is_moving - 1 == 0:  # если задержка на нуле и он хочет заканчивать движение
            self.is_moving = 0
            self.delay = random.randrange(1, 11) * 10
            self.random_x = 0
            self.random_y = 0
        # Дальше не требуется комментариев
        elif self.delay != 0 and self.is_moving == 0:
            self.delay -= 1
        elif self.is_moving != 0 and self.delay == 0:
            self.is_moving -= 1
        super(Ghoul, self).self_move()


class Zombie(Monster):
    """Класс Zombie. Создается зомби"""

    def __init__(self, player, center_pos, hp=50, reward=1, attack_range=200, running_speed=50, player_avoidance=True,
                 move_randomly=True, current_level=1):
        self.image = images.zombie_image
        self.images_stand = images.zombie_images_stand
        self.images_move = images.zombie_images_move
        gun = GUNS['Pistol'].copy() if current_level < 15 else GUNS[
            random.choice(['Pistol', 'ThroughShooter', 'Infinity'])].copy()
        gun.damage = 5 if current_level < 15 else 10
        gun.ammo = -1
        hp *= 2 if current_level >= 15 else 1
        gun.ammo_amount = -1
        gun.target_group = player_group
        gun.player = self
        gun.is_raised = True
        gun.fire_rate *= 3 if current_level < 15 else 2
        gun.bullet_speed = 50 if current_level < 5 else 100
        gun.can_be_raised = False
        if current_level >= 20:
            gun.damage = int(2 * self.active_gun.damage)
        elif current_level >= 10:
            gun.damage = int(1.5 * self.active_gun.damage)

        super(Zombie, self).__init__(player, center_pos, hp, reward, attack_range, gun, running_speed, player_avoidance,
                                     move_randomly, current_level)


class Bars(pygame.sprite.Sprite):
    """Класс Bars. Создается бар жизни монстра"""

    def __init__(self, owner, max_hp=100, bar_size=(30, 10), border_size=2, bar_color=(255, 0, 0), bg_color_1=(0, 0, 0),
                 bg_color_2=(128, 128, 128)):
        super().__init__()
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
        """Метод класса. Обновление бара"""
        if self.owner.hp_left == 0:
            self.kill()

        self.hp_left = self.owner.hp_left

        self.rect.x = self.owner.rect.centerx - self.bar_size[0] / 2
        self.rect.y = self.owner.cord_y - 20

        pygame.draw.rect(self.image, (64, 64, 64), (0, 0, self.bar_size[0], self.bar_size[1]), 0)
        pygame.draw.rect(self.image, (64, 0, 0), (self.border_size, self.border_size, self.bar_size[0] -
                                                  2 * self.border_size, self.bar_size[1] - 2 * self.border_size), 0)
        pygame.draw.rect(self.image, (255, 64, 64), (self.border_size, self.border_size, (self.bar_size[0] -
                                                                                          2 * self.border_size) *
                                                     self.hp_left / self.max_hp,
                                                     self.bar_size[1] - 2 * self.border_size), 0)


class Barrel(pygame.sprite.Sprite):
    """Класс Barrel. Создается бочка"""

    # id - 1260
    def __init__(self, x, y):
        super(Barrel, self).__init__(barrel_group)
        self.image = images.barrel_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

        self.probality = 5  # вероятность выпадение бутылки исцеления в проценте

    def draw(self, screen):
        """Метод класса. Отрисовка бочки"""
        screen.blit(self.image, self.rect)

    def move(self, x, y):
        """Метод класса. Движение бочки"""
        self.rect.x -= x
        self.rect.y -= y

    def is_collide(self, pers, x_speed, y_speed):
        """Метод класса. Коллизия между персонажем и бочкой"""
        height = pers.rect.height
        pers.rect.y += pers.rect.height // 1.5  # здесь не нужно, чтобы голова персонажа была над бочкой по координате у
        pers.rect.height -= pers.rect.height // 1.5
        self.rect.x -= x_speed
        if pygame.sprite.collide_rect(self, pers):
            self.rect.x += x_speed
            x_speed = 0
        else:
            self.rect.x += x_speed
        self.rect.y -= y_speed
        if pygame.sprite.collide_rect(self, pers):
            self.rect.y += y_speed
            y_speed = 0
        else:
            self.rect.y += y_speed
        pers.rect.height = height
        pers.rect.y -= pers.rect.height // 1.5
        return x_speed, y_speed

    def kill(self):
        """Метод класса. Удаление бочки"""
        a = random.randrange(101)
        if a <= self.probality:  # сперва надо создать бутылку исцеления для игрока, если повезет
            Heal(self.rect.x, self.rect.y)
        super(Barrel, self).kill()


class Torch(pygame.sprite.Sprite):
    """Класс Torch. Создается свечка(или свечки) или костер"""

    # id:
    # 1375 - torch is_collising
    # 1440 - torch not is_collising
    # 488 - candleA is_collising
    # 552 - candleA not is_collising
    # 614 - candleB is_collising
    # 549 - candleB not is_collising
    # is_collising - с коллизией
    # некоторые стоят на столбах и у них не надо проверять коллизию
    def __init__(self, filename, x, y, is_collising):
        super(Torch, self).__init__()
        if is_collising:
            torch_group.add(self)  # эта группа проверяет коллизию.
            # Иначе попадает группу, которая находится в классе комнаты
        if filename == 'torch_':
            self.images = images.torch_images
        elif filename == 'candleA_0':
            self.images = images.candlea_images
        else:
            self.images = images.candleb_images
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.cnt = 0  # счетчик для изменения спрайтов
        self.step = 10  # именно настолько увеличивается self.cnt
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        """Метод класса. Отрисовка свечки(или свечек) или костра"""
        screen.blit(self.image, self.rect)
        self._increment_cnt()

    def move(self, x, y):
        """Метод класса. Движение свечки(или свечек) или костра"""
        self.rect.x -= x
        self.rect.y -= y

    def _increment_cnt(self):
        """Метод класса. Увеличивает self.cnt для анимации спрайта"""
        self.image = self.images[self.cnt // self.step]
        self.cnt += 1
        if self.cnt >= 40:
            self.cnt = 0

    def is_collide(self, pers, x_speed, y_speed):
        """Метод класса. Проверяет коллизию между персонажем и свечкой"""
        pers.rect.y += pers.rect.height // 1.5  # Мы смотрим коллизию по ногам, а не по телу
        self.rect.x -= x_speed
        if pygame.sprite.collide_mask(self, pers):  # вот где понадобилась маска
            self.rect.x += x_speed
            x_speed = 0
        else:
            self.rect.x += x_speed
        self.rect.y -= y_speed
        if pygame.sprite.collide_mask(self, pers):
            self.rect.y += y_speed
            y_speed = 0
        else:
            self.rect.y += y_speed
        pers.rect.y -= pers.rect.height // 1.5
        return x_speed, y_speed


class Gate:
    """Класс Gate. Создаются ворота"""

    def __init__(self, x, y, orientation, top_or_bottom=''):
        self.map = pytmx.load_pygame(TILED_MAP_DIR + f'\\{orientation}_gate.tmx')
        # Чтобы не делать два файла ворот разных размеров (6*3 и 6*4), решил сделать так:
        self.top = True if top_or_bottom == 'top' else False
        self.x = x
        self.y = y
        self.height = self.map.height + (1 if self.top else 0)  # посмотрите на северные ворота и на южные
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.orientation = orientation  # горизонтальный или вертикальный
        self.cnt = 0  # счетчик для изменения спрайтов
        self.step = 60 // self.height  # именно настолько увеличивается self.cnt

    def move(self, x, y):
        """Метод класса. Движение ворот"""
        self.x -= x
        self.y -= y

    def render(self, screen, is_stay_gates):
        """Метод класса. Отрисовка ворот"""
        t = False
        for y in range(self.height):
            for x in range(1 if self.orientation == 'horizontal' else 0,
                           self.width - (1 if self.orientation == 'horizontal' else 0)):
                for layer in range(len(self.map.layers)):
                    if self.top and y >= 2:  # отрисовка 3 строки ворот
                        image = self.map.get_tile_image(x, y - 1, layer)
                    else:
                        image = self.map.get_tile_image(x, y, layer)
                    if image:
                        if self.orientation == 'horizontal' and self.cnt // self.step == y:
                            image = pygame.transform.chop(image, [0, int(self.tile_size * (self.cnt % self.step) /
                                                                         self.step), 0, self.tile_size - int(
                                self.tile_size * (self.cnt % self.step) / self.step)])
                            # chop для анимации поднятия ворот
                            t = True
                        if self.orientation == 'horizontal':
                            screen.blit(image, (self.x + self.tile_size * x, self.y + self.tile_size * y - int(
                                self.tile_size * self.cnt / self.step) + self.tile_size * self.height))
                        else:
                            screen.blit(image, (self.x + self.tile_size * x, self.y + self.tile_size * y))

            if t:
                self._increment_step(is_stay_gates)
                return

    def _increment_step(self, is_stay_gates):
        """Метод класса. Увеличивает self.cnt для анимации спрайта"""
        self.cnt += 1 if is_stay_gates and self.cnt < 60 else 0

    def is_collide(self, player, x_speed, y_speed, is_stay_gates):
        """Метод класса. Проверяет коллизию между персонажем и воротами"""
        if is_stay_gates and any([x_speed, y_speed]):
            if self.orientation == 'vertical':
                for y in range(self.height):
                    image = self.map.get_tile_image(0, y, 0)
                    if image:
                        x_speed, y_speed = is_collide_with_speed(player, image, self.x, self.y + y * self.tile_size,
                                                                 x_speed, y_speed)
            elif self.orientation == 'horizontal':
                for x in range(self.width):
                    image = self.map.get_tile_image(x, 2, 0)
                    if image:
                        x_speed, y_speed = is_collide_with_speed(player, image, x * self.tile_size + self.x,
                                                                 (3 if self.top else 2) * self.tile_size + self.y,
                                                                 x_speed, y_speed)
        return x_speed, y_speed


class Spike(pygame.sprite.Sprite):
    """Класс Gate. Создаются шипы"""

    # id - 1196
    def __init__(self, x, y):
        super(Spike, self).__init__()
        self.images = images.spike_images
        self.image = self.images[0]  # изображение нужное для коллизии
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.cnt = 0  # счетчик для изменения спрайтов
        self.step = 10  # именно настолько увеличивается self.cnt
        self.delay = 0

        self.damage = 5

    def draw(self, screen):
        """Метод класса. Отрисовка шипов"""
        screen.blit(self.image, self.rect)

    def move(self, x, y):
        """Метод класса. Движение шипов"""
        self.rect.x -= x
        self.rect.y -= y

    def increment_cnt(self):
        """Метод класса. Увеличивает self.cnt для анимации спрайта"""
        global spike_damage_delay
        if self.delay:
            self.delay -= 1
            return
        try:
            self.image = self.images[self.cnt // self.step]
        except IndexError:
            self.image = self.images[0]
        self.cnt += 1
        if self.cnt >= self.step * (len(self.images) - 1):
            self.cnt = 0
            self.image = self.images[0]
            self.delay = 60
            spike_damage_delay = 1

    def is_collide(self, player, is_stay_gates):
        """Метод класса. Коллизия шипов с персонажем(в основном с игроком)"""
        global spike_damage_delay
        if pygame.sprite.collide_rect(player, self) and spike_damage_delay and 6 >= self.images.index(self.image) >= 3 \
                and is_stay_gates:
            spike_damage_delay = 0
            player.take_damage(self.damage)


class Heal(pygame.sprite.Sprite):
    """Класс Heal. Создается бутылка, которая исцеляет игрока"""

    def __init__(self, x, y):
        super(Heal, self).__init__(heal_group)
        self.image = images.heal_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.cnt_heal = 35

    def move(self, x, y):
        """Метод класса. Движение бутылки исцеления"""
        self.rect.x -= x
        self.rect.y -= y

    def heal(self, player):
        """Метод класса. Игрок пьет бутылку и исцеляется.
        Пустая бутылка пропадает(можете представить что она разбилась"""
        player.hp_left += self.cnt_heal  # сперва лечит игрока
        player.hp_left = 100 if player.hp_left >= 100 else player.hp_left
        self.kill()

    def copy(self, center_pos=None):
        """Метод класса. Создается копия класса"""
        if center_pos is None:
            center_pos = (self.rect.x, self.rect.y)
        return Heal(*center_pos)


class Cell(pygame.sprite.Sprite):
    """Класс Cell. Создается экземпляр плитки, которая понадобится для коллизии других объектов.
    Она не нужна в отрисовке, но все равно нужно поддерживать"""

    def __init__(self, image, x, y):
        super(Cell, self).__init__(cell_group)
        if image:
            self.image = image
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.kill()

    def move(self, x, y):
        """Метод класса. Движение плиток. Нужно поддерживать реальное положение плитки"""
        self.rect.x -= x
        self.rect.y -= y


class DeadPerson(pygame.sprite.Sprite):
    """Класс DeadPerson. Создается анимация смерти персонажей"""

    def __init__(self, x, y, type_sprite):
        super(DeadPerson, self).__init__(dead_group)
        self.step = 10
        self.cnt = 0
        if type_sprite == 'Ghoul':
            self.images = images.ghoul_images_die
            self.rect = self.images[0].get_rect()
            self.rect.x = x
            self.rect.y = y
        elif type_sprite == 'Zombie':
            self.images = images.zombie_images_die
            self.rect = self.images[0].get_rect()
            self.rect.x = x
            self.rect.y = y
        else:
            self.kill()

    def move(self, x, y):
        """Метод класса. Движение мертвого персонажа"""
        self.rect.x -= x
        self.rect.y -= y

    def draw(self, screen):
        """Метод класса. Отрисовка мертвого персонажа"""
        if self.cnt >= len(self.images) * self.step + 50:
            self.kill()
        else:
            if self.cnt < len(self.images) * self.step:
                screen.blit(self.images[self.cnt // self.step], self.rect)
            else:
                screen.blit(self.images[-1], self.rect)
            self.cnt += 1


# Виды оружия:
GUNS = {
    'FirstGun': Gun(name='FirstGun', center_pos=(-100, -100), ammo=16, image=GUN_TEXTURES['Pistol'],
                    damage=15, bullet_image=images.BULLET_TEXTURES['DefaultBullet']),
    'Ak47': Gun(name='Ak47', image=GUN_TEXTURES['Ak47'], center_pos=(-100, -100), ammo=30, damage=15,
                bullet_color=(255, 255, 255), bullet_size=(5, 20), fire_rate=220, shooting_accuracy=0.95,
                bullet_image=images.BULLET_TEXTURES['DefaultBullet']),
    'Pistol': Gun(name='pistol', center_pos=(-10000, -10000), ammo=-1, image=GUN_TEXTURES['Pistol'], damage=5,
                  bullet_image=images.BULLET_TEXTURES['DefaultBullet'], fire_rate=600),
    'Fists': Gun(name='Fists', ammo=-1, damage=5, center_pos=(-10000, -10000), image=GUN_TEXTURES['Transperent'],
                 bullet_image=GUN_TEXTURES['Transperent']),
    'Uzi': Gun(name='Uzi', fire_rate=100, center_pos=(-100, -100), shooting_accuracy=0.75, damage=10, ammo=30,
               reload_time=500, image=GUN_TEXTURES['Uzi'], bullet_image=images.BULLET_TEXTURES['DefaultBulletGray']),
    'Sniper': Gun(name='Sniper', fire_rate=2000, damage=100, center_pos=(-100, -100), ammo=20,
                  reload_time=3000, bullet_color=(255, 128, 128), bullet_speed=600, image=GUN_TEXTURES['Sniper'],
                  bullet_image=images.BULLET_TEXTURES['DefaultBulletRustyCopper']),
    'GrenadeLauncher': Gun(name='GrenadeLauncher', center_pos=(-100, -100), fire_rate=1000,
                           shooting_accuracy=0.9, damage=30, damage_type='splash', splash_damage=30,
                           splash_radius=200, bullet_color=(64, 64, 196), image=GUN_TEXTURES['GrenadeLauncher'],
                           bullet_image=images.BULLET_TEXTURES['Grenade']),
    'BallLightningLauncher': Gun(name='BallLightningLauncher', center_pos=(-100, -100), fire_rate=100, damage=1000,
                                 ammo=1, reload_time=3500, destroy_bullets=False, bullet_color=(128, 128, 255),
                                 bullet_speed=50, bullet_size=(30, 30), image=GUN_TEXTURES['BallLightningLauncher'],
                                 bullet_image=images.BULLET_TEXTURES['BallLightning']),
    'Infinity': Gun(name='Infinity', fire_rate=300, center_pos=(-100, -100), damage=18, bullet_color=(196, 196, 64),
                    ammo=9999, image=GUN_TEXTURES['Infinity'],
                    bullet_image=images.BULLET_TEXTURES['DefaultBulletGold']),
    'MinePlacer': Gun(name='MiniPlacer', bullet_color=(196, 128, 64), center_pos=(-100, -100), damage=100,
                      bullet_speed=0, ammo=2, reload_time=4000, bullet_size=(20, 20), image=GUN_TEXTURES['MinePlacer'],
                      bullet_image=images.BULLET_TEXTURES['Mine'], damage_type='splash', splash_damage=50,
                      splash_radius=200),
    'ThroughShooter': Gun(name='ThroughShooter', bullet_color=(64, 64, 128), damage=7, ammo=50,
                          reload_time=4000, image=GUN_TEXTURES['ThroughShooter'], destroy_bullets=False,
                          bullet_image=images.BULLET_TEXTURES['LaserBullet']),
    'Shotgun': Shotgun(name='Shotgun', bullet_color=(64, 64, 128), damage=8, ammo=8, shooting_accuracy=0.85,
                       reload_time=2000, image=GUN_TEXTURES['Shotgun'], fire_rate=500,
                       bullet_image=images.BULLET_TEXTURES['CircleBullet']),
    'M4A4': Gun(name='M4A4', bullet_color=(128, 128, 128), damage=15, ammo=20, reload_time=3000,
                image=GUN_TEXTURES['M4A4'], bullet_speed=350, fire_rate=230,
                bullet_image=images.BULLET_TEXTURES['DefaultBulletGray']),
}
