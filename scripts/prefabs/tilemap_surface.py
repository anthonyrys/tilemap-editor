import pygame

def tilemap_surface(dimensions):
    name = 'tilemap_surface'
    strata = 1

    surface = pygame.Surface(dimensions).convert_alpha()
    surface.fill((1, 1, 1))
    surface.set_colorkey((0, 0, 0))
    
    rect = [300, 0]

    return {
        'name': name,
        'strata': strata,
        
        'surface': surface,
        'rect': pygame.Rect(rect[0], rect[1], *surface.get_size()),
        
        'color': (1, 1, 1)
    }
