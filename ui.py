import pygame
import os
import sprites

pygame.init()
shop_items_group = pygame.sprite.Group()

def load_image(name, path='ui'):
    fullname = os.path.join(path, name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    return image


def cut_image(image, start_pos, size):
    return image.subsurface(pygame.Rect(start_pos, size))


class Img(pygame.sprite.Sprite):
    def __init__(self, pos=(0, 0), image='main_ui.png', image_pos=(0, 0), image_size=(0, 0), sprite_group=[], scale=1):
        super().__init__(sprite_group)
        self.image = cut_image(load_image(image), image_pos, image_size)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * scale, self.image.get_height() * scale))
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
    def __init__(self, pos=(0, 0), image='main_ui.png', image_pos=(0, 0), image_size=(0, 0), sprite_group=[], scale=1):
        super().__init__(pos, image, image_pos, image_size, sprite_group, scale)

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
    
    def mouse_hovered(self):
        pass

    def mouse_clicked(self):
        pass


class Shop(pygame.sprite.Sprite):
    def __init__(self, sprite_group, pos, image_pos, image_size, image='main_ui.png'):
        super().__init__(sprite_group)

        self.sprite_group = sprite_group
        self.image = cut_image(load_image(image), image_pos, image_size)
        self.rect = self.image.get_rect()

        self.rect.x = pos[0]
        self.rect.y = pos[1]

        self.size = image_size

        self.items_list = []
        self.current_page = 0
        self.backgrounds = []

        self.button_back = Buttons(image_pos=(276, 114), image_size=(58, 26))
        self.button_next = Buttons(image_pos=(276, 84), image_size=(58, 26))

        page_counter_pos = (self.rect.x + self.image.get_width() / 2, self.rect.y + self.image.get_height() + 5)
        self.page_counter = Text(text=str(self.current_page), pos=page_counter_pos, sprite_group=(self.sprite_group))

        self.is_visible = False

        self.update_shop()
        self.update_items()
        self.update_page_counter()
    
    def flip_page(self, n):
        self.current_page += n
        self.update_backgrounds()
        self.update_items()
        self.update_page_counter()
    
    def set_page(self, n):
        self.current_page = n
        self.update_backgrounds()
        self.update_items()
        self.update_page_counter()

    def mouse_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def add_item(self, *items):
        for item in items:
            self.items_list.append(item)
            self.update_backgrounds()
            self.update_items()
    
    def remove_item(self, item):
        self.items_list.remove(item)
        self.update_backgrounds()
        self.update_items()
    
    def get_items(self):
        return self.items_list
    
    def set_visible(self, bool):
        self.is_visible = bool
        self.update_shop()
        self.update_backgrounds()
        self.update_items()            
        self.update_shop_buttons()
        self.update_page_counter()

    def update_shop(self):
        if self.is_visible:
            self.add(self.sprite_group)
        else:
            self.kill()
    
    def update_shop_buttons(self):
        if self.is_visible:
            self.button_back.add(self.sprite_group)
            self.button_next.add(self.sprite_group)

            self.button_back.rect.x = self.rect.x
            self.button_back.rect.y = self.rect.y + self.image.get_height()

            self.button_next.rect.x = self.rect.x + self.image.get_width() - self.button_next.image.get_width()
            self.button_next.rect.y = self.rect.y + self.image.get_height()
        else:
            self.button_back.kill()
            self.button_next.kill()
    
    def update_backgrounds(self):
        for bg in self.backgrounds:
            bg.kill()

        if self.is_visible:
            while len(self.backgrounds) < len(self.items_list):
                self.backgrounds.append(Buttons(image_pos=(214, 84), image_size=(58, 68), sprite_group=([])))
            for i in range(12):
                if len(self.backgrounds) - (12 * self.current_page + i) > 0:
                    self.backgrounds[12 * self.current_page + i].rect.x = self.rect.x + 14 + ((58 + 4) * (i % 3))
                    self.backgrounds[12 * self.current_page + i].rect.y = self.rect.y + 14 + ((68 + 4) * (i // 3))
                    self.backgrounds[12 * self.current_page + i].add(shop_items_group, self.sprite_group)
                    self.backgrounds[12 * self.current_page + i].item = self.items_list[12 * self.current_page + i]

                    price_tag = pygame.font.Font('ui/MinimalPixel v2.ttf', 10).render(str(self.items_list[12 * self.current_page + i].cost), 1, (255, 255, 255))
                    price_tag_rect = price_tag.get_rect()
                    price_tag_rect = (price_tag_rect[0] + 58 / 2 - price_tag.get_width() / 2, \
                        price_tag_rect[1] + 4, price_tag_rect[2], price_tag_rect[3])
                    self.backgrounds[12 * self.current_page + i].image.blit(price_tag, price_tag_rect)


    def update_items(self):
        for i in range(12):
            if len(self.backgrounds) - (12 * self.current_page + i) > 0:
                bg = self.backgrounds[12 * self.current_page + i]
                item_image = self.items_list[12 * self.current_page + i].content.image
                item_rect = (58 / 2 - item_image.get_width() / 2, \
                             68 / 2 - item_image.get_height() / 2 + 5, \
                             item_image.get_width(), item_image.get_height())
                bg.image.blit(item_image, item_rect)
    
    def update_page_counter(self):
        self.page_counter.kill()
        if self.is_visible:
            self.page_counter.add(self.sprite_group)
            self.page_counter.update_text(str(self.current_page + 1))

    def buy_item(self, item):
        if sprites.player_group.sprite.balance >= item.cost:
            sprites.player_group.sprite.balance -= item.cost
            gun = item.content.copy()
            gun.cord_x = sprites.player_group.sprite.cord_x
            gun.cord_y = sprites.player_group.sprite.cord_y

    def flip_shop_page(self):
        if self.button_next.mouse_clicked() and self.current_page + 1 <= len(self.items_list) // 12:
            self.flip_page(1)
        
        if self.button_back.mouse_clicked() and self.current_page - 1 >= 0:
            self.flip_page(-1)


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


class Inventory():
    def __init__(self, sprite_group):
        self.buttons = [Buttons(pos=(i * 65 + 300, 430), image_pos=(214, 156), image_size=(56, 56), sprite_group=sprite_group) for i in range(sprites.player_group.sprite.inventory_size)]
        self.update()
    
    def update(self):
        self.update_cells()
    
    def update_cells(self):
        for i, cell in enumerate(sprites.player_group.sprite.inventory):
            self.buttons[i].update_image(image='main_ui.png', image_pos=(214, 156), image_size=(56, 56))
            if cell != None:
                if cell == sprites.player_group.sprite.active_gun:
                    self.buttons[i].update_image(image='main_ui.png', image_pos=(274, 156), image_size=(56, 56))
                gun_rect = 29 - cell.rotate_image.get_rect()[2] / 2, 29 - cell.rotate_image.get_rect()[3] / 2, \
                    cell.rotate_image.get_rect()[2], cell.rotate_image.get_rect()[3] 
                self.buttons[i].image.blit(cell.rotate_image, gun_rect)
