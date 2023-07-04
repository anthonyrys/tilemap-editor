from scripts.services import load_spritesheet

import pygame
import os

class Fonts:
    FONT_PATH = os.path.join('imgs', 'fonts')

    FONT_KEYS = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.', ':', ',', ';', '\'', '\"', '(', '!', '?', ')', '+', '-', '*', '/', '=' 
    ]

    fonts = {
        'default': {
            'info': {
                'key_spacing': [10, 32],
                'key_padding': 5,

                'key_specials': {
                    'g': 11, 
                    'p': 11, 
                    'q': 11, 
                    'y': 11,

                    ':': -4
                }
            },

            'letters': {}
        }
    }
    
    def init():
        for font_file in os.listdir(Fonts.FONT_PATH):
            name = font_file.split('.')[0]
            imgs = load_spritesheet(os.path.join(Fonts.FONT_PATH, font_file))

            for index, key in enumerate(Fonts.FONT_KEYS):
                Fonts.fonts[name]['letters'][key] = imgs[index]

def create_text(text, color=(255, 255, 255), size=.5):
    text = text.lower()
    font = Fonts.fonts['default']
    
    surf_size = [0, 0]
    imgs = []

    for letter in text:
        img = None
        if letter == ' ':
            img = pygame.Surface((font['info']['key_spacing'][0], font['info']['key_spacing'][1])).convert_alpha()
            img.set_colorkey((0, 0, 0))

        else:
            img = font['letters'][letter].copy()        

        surf_size[0] += img.get_width() + font['info']['key_padding']
        if img.get_height() > surf_size[1]:
            surf_size[1] += img.get_height() * 2

        img = pygame.transform.scale(img, (img.get_width() * size, img.get_height() * size)).convert_alpha()
        img = pygame.mask.from_surface(img).to_surface(
            setcolor=color,
            unsetcolor=(0, 0, 0)
        ).convert_alpha()

        imgs.append(img)

    surf = pygame.Surface((surf_size[0] * size, surf_size[1] * size)).convert_alpha()
    surf.set_colorkey((0, 0, 0))

    x = 0
    for img, letter in zip(imgs, text):
        if letter in font['info']['key_specials'].keys():
            surf.blit(img, (x, (font['info']['key_specials'][letter] * size)))
            x += img.get_width() + (font['info']['key_padding'] * size)
            continue

        surf.blit(img, (x, 0))
        x += img.get_width() + (font['info']['key_padding'] * size)

    return surf
