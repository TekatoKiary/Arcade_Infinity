import pygame
import os

def load_image(name):
    fullname = os.path.join('ui', name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    return image


def cut_image(image, start_pos, size):
    return image.subsurface(pygame.Rect(start_pos, size))


class Img(pygame.sprite.Sprite):
    def __init__(self, pos=(0, 0), image='main_ui.png', image_pos=(0, 0), image_size=(0, 0), sprite_group=[]):
        super().__init__(sprite_group)
        self.image = cut_image(load_image(image), image_pos, image_size)
        self.rect = self.image.get_rect()

        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def mouse_hovered(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return True
        return False
    
    def update_image(self, image, image_pos, image_size):
        self.image = cut_image(load_image(image), image_pos, image_size)
    
    def get_image(self):
        return self.image


class Buttons(Img):
    def __init__(self, pos=(0, 0), image='main_ui.png', image_pos=(0, 0), image_size=(0, 0), sprite_group=[]):
        super().__init__(pos, image, image_pos, image_size, sprite_group)

    def mouse_clicked(self):
        if pygame.mouse.get_pressed()[0] == 1:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                return True
        return False


class Text(pygame.sprite.Sprite):
    def __init__(self, pos=(0, 0), text='Text', font='', size=(12), color=(255, 255, 255), sprite_group=[]):
        super().__init__(sprite_group)
        self.pos = pos
        self.text = str(text)
        self.font = font
        self.size = size
        self.color = color
        
        self.image = pygame.font.Font('ui/MinimalPixel v2.ttf', self.size).render(self.text, 1, self.color)
        self.rect = self.image.get_rect()
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
    
    def update_text(self, text):
        self.image = pygame.font.Font('ui/MinimalPixel v2.ttf', self.size).render(str(text), 1, self.color)
    
    def update_all(self, pos=(0, 0), text='Text', font='Times New Roman', size=(12), color=(255, 255, 255), sprite_group=[]):
        self.__init__(pos, text, font, size, color, sprite_group)


class Shop(pygame.sprite.Sprite):
    def __init__(self, sprite_group, pos, size, background, items_background):
        super().__init__(sprite_group)

        self.pos = pos
        self.size = size

        self.background = background
        self.items_background = items_background

        self.items_list = {}

        self.is_visible = False
    
    def add_item(self, item, cost: int):
        self.items_list[item] = cost
    
    def remove_item(self, item):
        self.items_list.pop(item, False)
    
    def get_items(self):
        return self.items_list
    
    def set_visible(self, bool):
        self.is_visible = bool
    
    def update(self):
        if self.is_visible:
            for item in self.items_list:
                item.rect.x = 0
