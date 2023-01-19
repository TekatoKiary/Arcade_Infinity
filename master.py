import pygame
import random
import os
import others
import pickle
import sys

pygame.init()  # инициализируем заранее чтобы не было проблем в images.py при загрузке изображений
pygame.display.set_caption('Arcade Infinity')
screen = pygame.display.set_mode(others.SIZE)

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)


# Комната 704*704
# протяженность коридора различна: длина вертикального - 608, горизонтального - 576. Но с учетом особенностями
# соединении с комнатами они выравниваются

# Ключевой момент: карта представляет собой квадрат 4*4, в котором комнаты случайно выбирают свои координаты.
# Следовательно, с учетом коридоров между ними карта получается с длиной около 4500 и такой шириной.
# Тогда размер 4500*4500.
# Координаты относительно квадрата 4*4 нужны только для комнат и коридоров.
# Другие классы используют координаты относительно этих же комнат за исключением немногих
class Labyrinth:
    """Класс Labyrinth. Создает карту комнат со своими объектами(например, такие декорации, как свеча).
    Проще говоря, это мозг игры, где происходит коллизия, движение, рендер и тому подобное"""

    def __init__(self):
        self.rooms = []
        self.corridors = []

        self.create_rooms()

    def create_rooms(self):
        """Метод класса. Создает комнаты. Во время создания на экране игры будет картинка загрузки"""
        # Возможно, вы скорее всего скажите что функцию можно переделать и что self.map_list не нужен.
        # НО self.map_list нужен для создания отображаемой карты для игрока. На данный момент мы не успели доделать его.
        loading()
        self.map_list = list([0] * 4 for _ in range(4))

        coords_all_room = []  # список координат комнат относительно self.map_list
        coords_hor_cor = []  # список координат горизонтальных коридоров относительно self.map_list
        coords_ver_cor = []  # список координат вертикальных коридоров относительно self.map_list

        x, y = random.randrange(4), random.randrange(4)  # Сперва создаем первую начальную комнату
        begin_room = room.Room(x, y, f'begin_room')
        coords_all_room.append((x, y))

        x_move = begin_room.x + (-others.WIDTH + begin_room.tile_size * begin_room.width) // 2
        y_move = begin_room.y + (-others.HEIGHT + begin_room.tile_size * begin_room.height) // 2

        self.map_list[y][x] = begin_room
        self.rooms.append(begin_room)
        for i in range(4):  # создание основной цепи комнат, то есть те комнаты, которые должны пройти
            d = [(0, -1), (0, 1), (1, 0), (-1, 0)]
            try:
                while 1:
                    kx, ky = random.choice(d)
                    if 4 > x + kx >= 0 and 4 > y + ky >= 0 and not self.map_list[y + ky][x + kx]:
                        if kx:
                            self.corridors.append(room.Corridor(min(x, x + kx), y, 'horizontal'))
                            coords_hor_cor.append((min(x, x + kx), y))
                        else:
                            self.corridors.append(room.Corridor(x, min(y, y + ky), 'vertical'))
                            coords_ver_cor.append((x, min(y, y + ky)))
                        x, y = x + kx, y + ky
                        r = room.Room(x, y, f'map{random.randrange(len(os.listdir(BAR_SPIKE_MAP_DIR)))}') \
                            if i < 3 else room.Room(x, y, f'end_room')  # r - room. Не хотел повторяться с room.py
                        r.add_monsters(player, current_level)
                        self.map_list[y][x] = r
                        self.rooms.append(r)
                        coords_all_room.append((x, y))
                        break
                    else:
                        del d[d.index((kx, ky))]
            except Exception:
                # Так как self.map_list это список списков 4*4, а комнат создают змейкой и их 5 штук,
                # то иногда предпоследняя комната может быть замурована тремя другими комнатами в углу.
                # Поэтому происходит пересоздание комнат
                self.clear_lab()
                self.create_rooms()
                return
        # Так как первоначально все комнаты с четырех сторон открыты,
        # то надо создавать стены или ворота, если есть коридор между комнатами:
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
        # Отображение надписи в начале уровня
        self.text_level = f'Level {current_level}'
        self.color = pygame.Color(255, 255, 255)  # его нужно менять потом
        # Надо передвигать все спрайты, так как мы сейчас в (0, 0) относительно self.map_list,
        # а начальная комната в (3, 2), например:
        self.move_objects(x_move, y_move)

    def update(self, screen):
        """Метод класса. Происходит рендер объектов, движение персонажей и коллизия определённых объектов"""

        x, y = move()
        player.move(x, y)
        x, y = self.render(x, y)  # рендер пола и непроходимых стен

        sprites.heal_group.draw(screen)
        player.draw(screen)
        [i.draw(screen) for i in sprites.gun_sprites]
        sprites.gun_sprites.update()
        sprites.bullet_group.draw(screen)
        sprites.bullet_group.update(room.is_stay_gates)
        [i.draw(screen) for i in torch_group]
        [i.draw(screen) for i in sprites.dead_group]

        x, y = self.render_passing_walls(x, y)  # рендер проходимой стеной и оставшихся объектов

        x, y = self.collision_with_torches(x, y)  # коллизия со свечками

        hsv = self.color.hsva
        if hsv[2] >= 10:  # Надпись 'Level {любое положительное число}' нужна только в начале
            self.color.hsva = (hsv[0], hsv[1], hsv[2] - 1, hsv[3])
            self.show_text_level()

        [i.new_wave(screen, player, current_level) for i in self.rooms]  # Создание новой волны монстров
        if x or y:  # если у игрока нет коллизии, то он может двигаться
            self.move_objects(x, y)

        sprites.ui_sprites.update()
        sprites.bar_sprites.update()
        sprites.bar_sprites.draw(screen)
        sprites.ui_sprites.draw(screen)

        # Коллизия пуль с бочками и стеной
        # хотелось через маску, но из-за оптимизации пришлось так:
        pygame.sprite.groupcollide(sprites.bullet_group, sprites.cell_group, True, False)
        pygame.sprite.groupcollide(sprites.bullet_group, sprites.barrel_group, True, True)

    def render(self, x, y):
        """Метод класса. Происходит рендер пола и непроходимой стеной"""
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
        """Метод класса. Происходит проходимой стеной и других объектов"""
        for room in self.rooms:
            if collide_rect(0, 0, others.WIDTH, others.HEIGHT,
                            room.x, room.y, room.x + room.width * room.tile_size,
                            room.y + room.height * room.tile_size):
                x, y = room.render_passing_walls(screen, x, y, player)
                # через условие проходят не все, поэтому для скорости отрисовки эта функция здесь:
                room.self_move_of_monster()
        [corridor.render_passing_walls(screen, player) for corridor in self.corridors if
         collide_rect(0, 0, others.WIDTH, others.HEIGHT, corridor.x, corridor.y,
                      corridor.x + corridor.width * corridor.tile_size,
                      corridor.y + corridor.height * corridor.tile_size)]
        return x, y

    def collision_with_torches(self, x, y):
        """Метод класса. Проверка коллизии игрока со свечками"""
        for i in torch_group:
            if not any([x, y]):
                break
            x, y = i.is_collide(player, x, y)
        return x, y

    def move_objects(self, x, y):
        """Метод класса. Движение объектов"""
        [i.move(x, y) for i in self.rooms]
        [i.move(x, y) for i in self.corridors]
        [i.move(x, y) for i in torch_group]
        [i.move(x, y) for i in heal_group]
        [i.move(x, y) for i in sprites.cell_group]
        [i.move(x, y) for i in sprites.gun_sprites]
        [i.move(x, y) for i in sprites.bullet_group]
        [i.move(x, y) for i in sprites.dead_group]

    def enter_next_level(self):
        """Метод класса. Завершение уровня"""
        global current_level
        end_room = self.rooms[4]
        if collide_rect(0, 0, others.WIDTH, others.HEIGHT,
                        end_room.x, end_room.y, end_room.x + end_room.width * end_room.tile_size,
                        end_room.y + end_room.height * end_room.tile_size) and end_room.enter_next_level(player):
            self.clear_lab()
            current_level += 1
            game_save(current_save_id)
            self.create_rooms()

    def clear_lab(self):
        """Метод класса. Удаление всех объектов"""
        [i.clear() for i in self.rooms]
        self.rooms.clear()
        self.corridors.clear()
        [i.kill() for i in sprites.torch_group]
        [i.kill() for i in sprites.cell_group]
        [i.kill() for i in sprites.heal_group]
        [i.kill() for i in sprites.dead_group]
        [i.kill() for i in sprites.bar_sprites]
        [i.kill() for i in sprites.gun_sprites]
        [i.kill() for i in sprites.bullet_group]

    def show_text_level(self):
        """Метод класса. Отображение надписи, на каком ты сейчас уровне, в начале игры"""
        font = pygame.font.Font('ui/MinimalPixel v2.ttf', 30).render(self.text_level, True, self.color)
        screen.blit(font, (others.WIDTH // 2 - font.get_width() // 2, 150))


def update_hp_bar(bar, health_percent):  # обновляет информацию о здоровье игрока
    health_percent = max(0, min(1, health_percent))
    size_delta = (1 - health_percent) * 94
    bar.update_image(image='main_ui.png', image_pos=(214 + size_delta, 0), image_size=(96 - size_delta, 18))

    if health_percent <= 0:
        forced_save_update(current_save_id)
        set_game_over(True)


def update_player_balance(sprite):  # обновляет информацию о кол-во денег(балансе) игрока
    sprite.update_text(text=player.balance)


def update_player_ammo(sprite):  # обновляет информацию о кол-во патронов игрока
    if player.active_gun.is_reloading_now:
        sprite.update_text(text=f'reloading..')
    else:
        sprite.update_text(text=f'{player.active_gun.ammo_amount} / {player.active_gun.ammo}')


def open_shop():  # открывает или закрывает магазин
    shop.set_visible(not shop.is_visible)
    shop.set_page(0)


def loading():  # Экран загрузки. Нужен во время создания карты и других объектов
    image = load_image('main_menu_bg2.png')
    image = pygame.transform.scale(image, (others.WIDTH, others.HEIGHT))
    screen.blit(image, (0, 0))
    font = pygame.font.Font('ui/MinimalPixel v2.ttf', 30).render('loading...', True, (255, 255, 255))
    screen.blit(font, (others.WIDTH - font.get_width() - 20, others.HEIGHT - font.get_height() - 20))
    pygame.display.update()


def move():  # Движение игрока
    key = pygame.key.get_pressed()
    x, y = 0, 0
    if key[pygame.K_w]:
        y = -10
    if key[pygame.K_s]:
        y = 10
    if key[pygame.K_a]:
        x = -10
    if key[pygame.K_d]:
        x = 10
    return x, y


def forced_save_update(saveid):
    data = {}
    data['player_inventory'] = ['FirstGun', None, None]
    data['player_balance'] = 0
    data['player_hp'] = 100
    data['level'] = 1
    with open(f"saves/save_{saveid}.bin", "wb") as fp:
        pickle.dump(data, fp)


def game_save(saveid, set_to_default=False):
    data = {}
    if not set_to_default:
        data['player_inventory'] = [i.name if i else None for i in player.inventory]
        data['player_balance'] = player.balance
        data['player_hp'] = player.hp_left
        data['level'] = current_level
        with open(f"saves/save_{saveid}.bin", "wb") as fp:
            pickle.dump(data, fp)
    else:
        forced_save_update(saveid)


def game_load(saveid):
    with open(f"saves/save_{saveid}.bin", "rb") as fp:
        return pickle.load(fp)


def change_save(save_id):
    global current_save_id
    current_save_id = save_id


def init_sprites():
    global current_level
    try:
        player_stats = game_load(current_save_id)
    except Exception:
        forced_save_update(current_save_id)
    player.hp_left = player_stats['player_hp']
    player.balance = player_stats['player_balance']
    player.set_inventory([GUNS[i].copy() if i else None for i in player_stats['player_inventory']])
    current_level = player_stats['level']
    player.set_current_level(current_level)


if __name__ == '__main__':
    from others import collide_rect, FPS, BAR_SPIKE_MAP_DIR
    from images import load_image
    import sprites
    from sprites import torch_group, heal_group, Heal, GUNS
    import ui
    import room

    clock = pygame.time.Clock()
    running = 1

    current_save_id = 1
    current_level = 1

    player = sprites.Player()

    # Ui
    player_info = ui.Img(pos=(20, 20), sprite_group=(sprites.all_sprites, sprites.ui_sprites), image_pos=(56, 0),
                         image_size=(154, 48))
    player_icon = pygame.transform.scale(player.image, (player.image.get_width() / 1.5,
                                                        player.image.get_height() / 1.5))
    player_info.image.blit(player_icon, (13, 12, player.image.get_width(), player.image.get_height()))
    player_hp_bar = ui.Img(pos=(20 + 54, 20 + 4), image_pos=(214, 0), image_size=(94, 18),
                           sprite_group=(sprites.all_sprites, sprites.ui_sprites))
    shop_button = ui.Buttons(pos=(720, 20), sprite_group=(sprites.all_sprites, sprites.ui_sprites), image_pos=(138, 52),
                             image_size=(65, 28))
    player_balance = ui.Text(pos=(90, 50), sprite_group=sprites.ui_sprites)
    player_ammo = ui.Text(pos=(others.WIDTH - 120, others.HEIGHT - 40), sprite_group=sprites.ui_sprites, size=20)

    # Shop
    shop = ui.Shop(player=player, pos=(590, 60), image_pos=(0, 84), image_size=(210, 312),
                   sprite_group=(sprites.ui_sprites, sprites.all_sprites))
    # Тестовое добавление товаров в магазин
    Uzi = ui.ShopItems(GUNS['Uzi'], 50)
    Sniper = ui.ShopItems(GUNS['Sniper'], 1500)
    GrenadeLauncher = ui.ShopItems(GUNS['GrenadeLauncher'], 700)
    BallLightningLauncher = ui.ShopItems(GUNS['BallLightningLauncher'], 900)
    Infinity = ui.ShopItems(GUNS['Infinity'], 450)
    MinePlacer = ui.ShopItems(GUNS['MinePlacer'], 400)
    Ak47 = ui.ShopItems(GUNS['Ak47'], 500)
    Pistol = ui.ShopItems(GUNS['FirstGun'], 50)
    heal = ui.ShopItems(Heal(0, 0), 100)
    ThroughShooter = ui.ShopItems(GUNS['ThroughShooter'], 900)
    Shotgun = ui.ShopItems(GUNS['Shotgun'], 650)
    M4A4 = ui.ShopItems(GUNS['M4A4'], 550)  # Дороже АК47 из-за урона 15 > 10

    shop_items = [heal, Pistol, Uzi, Infinity, Shotgun, Ak47, GrenadeLauncher, MinePlacer, ThroughShooter,
                  BallLightningLauncher, M4A4, Sniper]

    shop.add_item(*shop_items)


    def set_game_paused(flag):
        global game_paused
        if flag:
            game_paused = True
            for sprite in pause_group:
                sprite.add(sprites.all_sprites)
        else:
            game_paused = False
            for sprite in pause_group:
                sprites.all_sprites.remove(sprite)


    def set_game_started(flag):
        global game_started
        if flag:
            game_started = True
            for sprite in main_menu_group:
                sprite.kill()
                sprite.add(main_menu_group)
        else:
            game_started = False


    def set_loading_menu_opened(flag):
        global loading_menu_opened
        if flag:
            loading_menu_opened = True
            for sprite in loading_menu_sprites:
                sprite.add(main_menu_group)
        else:
            loading_menu_opened = False
            for sprite in loading_menu_sprites:
                main_menu_group.remove(sprite)


    def set_game_over(flag):
        global game_over
        if flag:
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

    main_menu_bg = ui.Img(pos=(0, 0), image='pause.png', image_pos=(0, 0), image_size=(800, 500),
                          sprite_group=pause_group)

    resume_button = ui.Buttons(pos=(345, 180), image_pos=(214, 216), image_size=(65, 28), sprite_group=pause_group,
                               scale=2)
    exit_button_on_pause = ui.Buttons(pos=(345, 240), image_pos=(214, 248), image_size=(65, 28),
                                      sprite_group=pause_group, scale=2)

    ui.Text(pos=(30, 340), sprite_group=pause_group, text='press W, A, S, D to move', size=14)
    ui.Text(pos=(30, 370), sprite_group=pause_group, text='press F to take the gun', size=14)
    ui.Text(pos=(30, 400), sprite_group=pause_group, text='press G to drop the gun', size=14)
    ui.Text(pos=(30, 430), sprite_group=pause_group, text='press E to take the heal', size=14)
    ui.Text(pos=(30, 460), sprite_group=pause_group, text='press Enter to the next level', size=14)

    # Main menu
    main_menu_bg = ui.Img(pos=(0, 0), image='main_menu_bg2.png', image_pos=(0, 0), image_size=(800, 500),
                          sprite_group=main_menu_group)

    start_game_button = ui.Buttons(pos=(345, 180), image_pos=(0, 52), image_size=(65, 28),
                                   sprite_group=main_menu_group, scale=2)
    load_game_button = ui.Buttons(pos=(345, 240), image_pos=(69, 52), image_size=(65, 28),
                                  sprite_group=main_menu_group, scale=2)
    exit_button_on_main_menu = ui.Buttons(pos=(345, 300), image_pos=(214, 248), image_size=(65, 28),
                                          sprite_group=main_menu_group, scale=2)

    # Loading menu
    loading_menu_background = ui.Img(pos=(250, 110), image_pos=(0, 400), image_size=(152, 132),
                                     sprite_group=loading_menu_sprites, scale=2)
    save1 = ui.Buttons(pos=(335, 150), image_pos=(214, 280), image_size=(65, 28), sprite_group=loading_menu_sprites,
                       scale=2)
    save2 = ui.Buttons(pos=(335, 210), image_pos=(214, 312), image_size=(65, 28), sprite_group=loading_menu_sprites,
                       scale=2)
    save3 = ui.Buttons(pos=(335, 270), image_pos=(214, 344), image_size=(65, 28), sprite_group=loading_menu_sprites,
                       scale=2)
    back_to_main_menu_button = ui.Buttons(pos=(335, 380), image_pos=(283, 280), image_size=(65, 28),
                                          sprite_group=loading_menu_sprites, scale=2)
    current_save = ui.Text(pos=(385, 150), text=f"save {current_save_id}", sprite_group=main_menu_group, size=14)
    # game lost

    game_over_bg = ui.Img(pos=(0, 0), image='game_over.png', image_pos=(0, 0), image_size=(800, 500),
                          sprite_group=game_over_sprites)
    restart_button = ui.Buttons(pos=(325, 200), image_pos=(283, 216), image_size=(65, 28),
                                sprite_group=game_over_sprites, scale=2)
    exit_button_on_game_over = ui.Buttons(pos=(325, 260), image_pos=(214, 248), image_size=(65, 28),
                                          sprite_group=game_over_sprites, scale=2)

    game_started = False
    game_paused = False
    loading_menu_opened = False
    game_over = False

    set_game_started(False)
    # ________________________

    while running:
        if not game_started:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not loading_menu_opened:
                        if start_game_button.mouse_clicked():
                            init_sprites()
                            lab = Labyrinth()
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
            screen.fill((0, 0, 0))
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
                        lab.clear_lab()
                        set_game_paused(False)
                        set_game_started(False)
                        shop.set_visible(False)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        set_game_paused(False)

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
                        lab.clear_lab()
                    if restart_button.mouse_clicked():
                        lab.clear_lab()
                        forced_save_update(current_save_id)
                        init_sprites()
                        lab = Labyrinth()
                        set_game_over(False)
            game_over_sprites.draw(screen)
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        heal = pygame.sprite.spritecollide(player, heal_group, False)
                        if heal:
                            heal[0].heal(player)  # персонаж увеличивает здоровье
                    if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                        lab.enter_next_level()
                    if event.key == pygame.K_ESCAPE:
                        set_game_paused(True)
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

                            if pause_button.mouse_clicked():
                                set_game_paused(True)
                    # ===============================================================================
                    # Проверка нажатия на кнопку покупки
                    for bg in shop.backgrounds:
                        if bg.mouse_clicked() and shop.is_visible and bg in sprites.all_sprites:
                            shop.buy_item(bg.item)
                    if can_shoot:
                        player.on_clicked(event)

                    # Проверка нажатия на ячейки инвентаря
                    for i, button in enumerate(player.cells.buttons):
                        if button.mouse_clicked():
                            player.switch_gun(i)
                    # ===============================================================================

                if event.type == pygame.KEYDOWN:
                    player.on_k_pressed(event)

                # Перезарядка текущего оружия
                if event.type == player.active_gun.reload_event:
                    player.active_gun.reload_ammo()
                    pygame.time.set_timer(player.active_gun.reload_event, 0)

                # Стрельба
                if event.type == player.active_gun.shoot_event:
                    if pygame.mouse.get_pressed()[0]:
                        player.active_gun.shoot(target_pos=pygame.mouse.get_pos())
                    else:
                        pygame.time.set_timer(player.active_gun.shoot_event, 0)
                        player.active_gun.can_shoot = True

            screen.fill((0, 0, 0))

            lab.update(screen)

            update_hp_bar(player_hp_bar, player.hp_left / player.max_hp)
            update_player_balance(player_balance)
            update_player_ammo(player_ammo)
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()

# для pyinstaller
# pyinstaller --add-data="textures/;textures/" --add-data="ui/;ui/" --add-data="map/;map/" --add-data="saves/;saves/"
# --noconsole --onefile master.py --icon="adventurer_stand.ico"
