import pygame
import os
import random
import player
import math


class Player(pygame.sprite.Sprite):
    def __init__(self, center_pos):
        super().__init__(all_sprites)
        self.add(player_sprite)

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


class Gun(pygame.sprite.Sprite):
    def __init__(self, center_pos):
        super().__init__(all_sprites)
        self.add(gun_sprites)

        self.image = pygame.Surface((25, 25), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, (128, 255, 128), (0, 0, 25, 25), 0)

        self.rect.x = center_pos[0] - 25 // 2
        self.rect.y = center_pos[1] - 25 // 2

        self.cord_x = self.rect.x
        self.cord_y = self.rect.y

    def update(self):
        self.rect.x = self.cord_x
        self.rect.y = self.cord_y

        if pygame.sprite.spritecollide(self, player_sprite, False):
            self.cord_x = pl.cord_x + 30
            self.cord_y = pl.cord_y + 20

    def rotate(self):
        pass

    def shoot(self):
        pass


all_sprites = pygame.sprite.Group()
player_sprite = pygame.sprite.Group()
gun_sprites = pygame.sprite.Group()


def k_pressed():
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        pl.cord_y -= 50 / 60
    if keys[pygame.K_a]:
        pl.cord_x -= 50 / 60
    if keys[pygame.K_s]:
        pl.cord_y += 50 / 60
    if keys[pygame.K_d]:
        pl.cord_x += 50 / 60


pl = Player((100, 100))
gun = Gun((200, 200))

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

        k_pressed()

        screen.fill((0, 0, 0))

        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()
