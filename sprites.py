import pygame
import others
from others import load_image


class Player(pygame.sprite.Sprite):
    # Временно
    def __init__(self, ):
        super(Player, self).__init__()
        self.image = load_image('Adventurer\\adventurer_stand.png', -1)
        self.image = pygame.transform.scale(self.image,
                                            (30, self.image.get_rect().height * 2))
        self.rect = self.image.get_rect()
        self.rect.x = self.x = others.WIDTH // 2
        self.rect.y = self.y = others.HEIGHT // 2
        image = pygame.transform.scale(self.image,
                                       (30, self.image.get_rect().height - self.rect.height // 1.01))
        self.mask = pygame.mask.from_surface(image)  # маска нужна для коллизии с бочками
        # Зачем создавать новый image: если заметить, то оставлена только та часть, где должны быть ноги.
        # И для того, чтобы точно это были ноги, а не прическа, в другой функции меняется координату у

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def move(self):
        self.rect.x = self.x = others.WIDTH // 2 - self.rect.width // 2
        self.rect.y = self.y = others.HEIGHT // 2 - self.rect.height // 2


class Barrel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Barrel, self).__init__()
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
