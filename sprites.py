import pygame
import others
from others import load_image

barrel_group = pygame.sprite.Group()
torch_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    # Временно
    def __init__(self, ):
        super(Player, self).__init__()
        self.image = load_image('Adventurer\\adventurer_stand_prob_0.png', -1)
        self.image = pygame.transform.scale(self.image,
                                            (30, self.image.get_rect().height * 2.3))
        self.images = [pygame.transform.scale(load_image(f'Adventurer\\adventurer_stand_prob_{i}.png', -1),
                                              (30, self.image.get_rect().height))
                       for i in range(13)]
        self.rect = self.image.get_rect()
        self.rect.x = self.x = others.WIDTH // 2
        self.rect.y = self.y = others.HEIGHT // 2
        image = pygame.transform.scale(self.image,
                                       (30, self.image.get_rect().height - self.rect.height // 1.01))
        self.mask = pygame.mask.from_surface(image)  # маска нужна для коллизии с бочками
        # Зачем создавать новый image: если заметить, то оставлена только та часть, где должны быть ноги.
        # И для того, чтобы точно это были ноги, а не прическа, в другой функции меняется координату у
        self.cnt = 0
        self.step = 10

    def draw(self, screen):
        # screen.blit(self.image, self.rect)
        screen.blit(self.images[self.cnt // self.step], self.rect)

    def move(self):
        self.rect.x = self.x = others.WIDTH // 2 - self.rect.width // 2
        self.rect.y = self.y = others.HEIGHT // 2 - self.rect.height // 2
        self.cnt += -self.cnt if self.cnt >= 120 else 1


class Barrel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Barrel, self).__init__(barrel_group)
        self.image = load_image('cub.png', -1)
        self.image = pygame.transform.scale(self.image, (28, 32))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def move(self, x, y):
        self.rect.x -= x
        self.rect.y -= y

    def is_collide(self, player, x_speed, y_speed):
        player.rect.y += player.rect.height // 1.01  # Мы смотрим коллизию по ногам, а не по телу
        self.rect.x -= x_speed
        if pygame.sprite.collide_mask(self, player):  # вот где понадобилась маска
            self.rect.x += x_speed
            x_speed = 0
        else:
            self.rect.x += x_speed
        self.rect.y -= y_speed
        if pygame.sprite.collide_mask(self, player):
            self.rect.y += y_speed
            y_speed = 0
        else:
            self.rect.y += y_speed
        player.rect.y -= player.rect.height // 1.01
        return x_speed, y_speed


class Torch(pygame.sprite.Sprite):

    # id:
    # 1375 - torch is_collising
    # 1440 - torch not is_collising
    # 488 - candleA is_collising
    # 552 - candleA not is_collising
    # 614 - candleB is_collising
    # 549 - candleB not is_collising
    def __init__(self, filename, x, y, is_collising):
        super(Torch, self).__init__()
        if is_collising:
            torch_group.add(self)
        self.images = [pygame.transform.scale(load_image(f'Catacombs\\{filename}{i}.png', -1),
                                              (32 if filename != 'candleA_0' else 16, 32))
                       for i in range(1, 5)]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.cnt = 0
        self.step = 10
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def move(self, x, y):
        self.rect.x -= x
        self.rect.y -= y

    def increment_cnt(self):
        self.image = self.images[self.cnt // self.step]
        self.cnt += 1
        if self.cnt >= 40:
            self.cnt = 0

    def is_collide(self, player, x_speed, y_speed):
        player.rect.y += player.rect.height // 1.01  # Мы смотрим коллизию по ногам, а не по телу
        self.rect.x -= x_speed
        if pygame.sprite.collide_mask(self, player):  # вот где понадобилась маска
            self.rect.x += x_speed
            x_speed = 0
        else:
            self.rect.x += x_speed
        self.rect.y -= y_speed
        if pygame.sprite.collide_mask(self, player):
            self.rect.y += y_speed
            y_speed = 0
        else:
            self.rect.y += y_speed
        player.rect.y -= player.rect.height // 1.01
        return x_speed, y_speed


class Spike(pygame.sprite.Sprite):

    # id:

    def __init__(self, x, y):
        super(Spike, self).__init__(spike_group)
        self.images = [pygame.transform.scale(load_image(f'Catacombs\\spike_{i}.png', -1),
                                              (32, 32))
                       for i in range(5)]
        self.images.extend([pygame.transform.scale(load_image(f'Catacombs\\spike_{i}.png', -1),
                                                   (32, 32))
                            for i in range(4, 0, -1)])
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.cnt = 0
        self.step = 10
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def move(self, x, y):
        self.rect.x -= x
        self.rect.y -= y

    def increment_cnt(self):
        try:
            self.image = self.images[self.cnt // self.step]
        except IndexError:
            self.image = self.images[0]
        self.cnt += 1
        if self.cnt >= 180:
            self.cnt = 0

    def is_collide(self, player, x_speed, y_speed):
        # пока в разработке
        pass
