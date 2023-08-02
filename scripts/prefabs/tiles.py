import pygame

def tile_interface(position, image, orientation, flipped, tileset, index, tile, strata):
    name = f'tile_interface--{tileset}_{index}'
    strata = strata

    surface = image
    surface = pygame.transform.rotate(surface, -orientation)
    surface = pygame.transform.flip(surface, flipped, False)
    
    rect = position

    return {
        'name': name,
        'surface': surface,

        'rect': pygame.Rect(rect[0], rect[1], *surface.get_size()),
        'dimensions': surface.get_size(),
        'orientation': orientation,
        'flipped': flipped,
        
        'tileset': tileset,
        'index': index,
        
        'tile': tile,
        'strata': strata,
    }

def tile_tilemap(position, image, orientation, flipped, tileset, index, tile, strata):
    name = f'tile_tilemap--{tileset}_{index}'
    strata = strata

    surface = image
    surface = pygame.transform.rotate(surface, -orientation)
    surface = pygame.transform.flip(surface, flipped, False)
    
    rect = position

    return {
        'name': name,
        'surface': surface,

        'rect': pygame.Rect(rect[0], rect[1], *surface.get_size()),
        'dimensions': surface.get_size(),
        'orientation': orientation,
        'flipped': flipped,
        
        'tileset': tileset,
        'index': index,
        
        'tile': tile,
        'strata': strata,
    }
