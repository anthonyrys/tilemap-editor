from scripts import SCREEN_DIMENSIONS

import pygame

def sidebar():
    name = 'sidebar'
    strata = 1

    surface = pygame.Surface((300, SCREEN_DIMENSIONS[1])).convert_alpha()
    surface.fill((14, 14, 14))
    surface.set_colorkey((0, 0, 0))
    
    rect = [0, 0]

    return {
        'name': name,
        'strata': strata,
        
        'surface': surface,
        'rect': pygame.Rect(rect[0], rect[1], *surface.get_size()),

        'color': (14, 14, 14)
    }
