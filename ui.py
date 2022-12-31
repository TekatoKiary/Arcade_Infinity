import pygame
import os

pygame.init()
shop_group = pygame.sprite.Group()
shop_items_group = pygame.sprite.Group()

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
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def update_image(self, image, image_pos, image_size):
        self.image = cut_image(load_image(image), image_pos, image_size)
    
    def get_image(self):
        return self.image


class Buttons(Img):
    def __init__(self, pos=(0, 0), image='main_ui.png', image_pos=(0, 0), image_size=(0, 0), sprite_group=[]):
        super().__init__(pos, image, image_pos, image_size, sprite_group)

    def mouse_clicked(self):
        if pygame.mouse.get_pressed()[0] == 1:
            return self.rect.collidepoint(pygame.mouse.get_pos())


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
    def __init__(self, sprite_group, pos, image_pos, image_size, image='main_ui.png'):
        super().__init__(sprite_group, shop_group)

        self.sprite_group = sprite_group
        self.image = cut_image(load_image(image), image_pos, image_size)
        self.rect = self.image.get_rect()

        self.rect.x = pos[0]
        self.rect.y = pos[1]

        self.size = image_size

        self.items_list = []
        self.page = 0
        self.backgrounds = []

        self.is_visible = False

        self.update_shop()
        self.update_items()
    
    def flip_page(self, n):
        self.page += n
    
    def set_page(self, n):
        self.page = n

    def mouse_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def add_item(self, item):
        self.items_list.append(item)
        self.update_backgrounds()
        self.update_items()
    
    def remove_item(self, item):
        return self.items_list.remove(item)
    
    def get_items(self):
        return self.items_list
    
    def set_visible(self, bool):
        self.is_visible = bool
        self.update_shop()
        self.update_backgrounds()
        self.update_items()            
    
    def update_shop(self):
        if self.is_visible:
            self.add(self.sprite_group)
        else:
            self.kill()
    
    def update_backgrounds(self):
        if self.is_visible:
            while len(self.backgrounds) < len(self.items_list):
                self.backgrounds.append(Buttons(image_pos=(214, 84), image_size=(58, 68), sprite_group=([])))
            for i in range(12):
                if len(self.backgrounds) - (12 * self.page + i) > 0:
                    self.backgrounds[12 * self.page + i].rect.x = self.rect.x + 14 + ((58 + 4) * (i % 3))
                    self.backgrounds[12 * self.page + i].rect.y = self.rect.y + 14 + ((68 + 4) * (i // 3))
                    self.backgrounds[12 * self.page + i].add(shop_items_group, self.sprite_group)
                    self.backgrounds[12 * self.page + i].item = self.items_list[12 * self.page + i]

                    price_tag = pygame.font.Font('ui/MinimalPixel v2.ttf', 10).render(str(self.items_list[12 * self.page + i].cost), 1, (255, 255, 255))
                    price_tag_rect = price_tag.get_rect()
                    price_tag_rect = (price_tag_rect[0] + 58 / 2 - price_tag.get_width() / 2, \
                        price_tag_rect[1] + 4, price_tag_rect[2], price_tag_rect[3])
                    self.backgrounds[12 * self.page + i].image.blit(price_tag, price_tag_rect)

        else:
            for bg in self.backgrounds:
                bg.kill()

    def update_items(self):
        for i in range(12):
            if len(self.backgrounds) - (12 * self.page + i) > 0:
                bg = self.backgrounds[12 * self.page + i]
                item_image = self.items_list[12 * self.page + i].content.image
                item_rect = (58 / 2 - item_image.get_width() / 2, \
                             68 / 2 - item_image.get_height() / 2 + 5, \
                             item_image.get_width(), item_image.get_height())
                bg.image.blit(item_image, item_rect)


class ShopItems():
    def __init__(self, content, cost):
        content.kill()
        self.content = content
        self.cost = cost
    
    def set_data(self, content, cost):
        content.kill()
        self.content = content
        self.cost = cost
    
    def set_item(self, content):
        content.kill()
        self.content = content

    def set_cost(self, cost):
        self.cost = cost
    
    # def update_items(self):
    #     while len(self.backgrounds) < len(self.items_list):
    #         self.backgrounds.append(Buttons(image_pos=(214, 84), image_size=(58, 68), sprite_group=(self.general_sprite_group, shop_items_group)))

    #     for bg in self.backgrounds:
    #         bg.kill()

    #     for item in self.items_list:
    #         self.general_sprite_group.remove(item)
    #         item.can_be_raised = False
        
    #     if self.is_visible:
    #         i = -1
    #         for item in self.items_list:
    #             # if not pygame.sprite.spritecollide(self, shop_items_group, False):
    #             if True:
    #                 i += 1
                    
    #                 bg_width = self.backgrounds[i].image.get_width()
    #                 bg_height = self.backgrounds[i].image.get_height()
                    
    #                 self.backgrounds[i].add(self.general_sprite_group, shop_items_group)
    #                 self.backgrounds[i].rect.x = self.rect.x + 14 + ((bg_width + 4) * (i % 3))
    #                 self.backgrounds[i].rect.y = self.rect.y + 14 + ((bg_height + 4) * (i // 3))
    #                 item_img_rect = item.image.get_rect()
    #                 item_img_rect.x += bg_width / 2 - item.image.get_width() / 2
    #                 item_img_rect.y += 5 + bg_height / 2 - item.image.get_height() / 2
    #                 self.backgrounds[i].image.blit(item.image, item_img_rect)
    #                 self.backgrounds[i].cost = int(self.items_list[item])
    #                 self.backgrounds[i].item = item

    #                 item.cord_x = self.rect.x + 14 + bg_width / 2 - item.image.get_width() / 2 + (bg_width * (i % 3))
    #                 item.cord_y = self.rect.y + 14 + bg_height / 2 - item.image.get_height() / 2 + (bg_height * (i // 3))


                    


                




                       





