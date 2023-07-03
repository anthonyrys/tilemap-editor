import pygame

def tile_interface(position, image, orientation, tileset, index, tile, strata):
    name = f'tile_interface--{tileset}_{index}'
    strata = strata

    surface = image
    surface = pygame.transform.rotate(surface, -orientation)
    
    rect = position

    return {
        'name': name,
        'surface': surface,

        'rect': pygame.Rect(rect[0], rect[1], *surface.get_size()),
        'dimensions': surface.get_size(),
        'orientation': orientation,
        
        'tileset': tileset,
        'index': index,
        
        'tile': tile,
        'strata': strata,
    }

def tile_tilemap(position, image, orientation, tileset, index, tile, strata):
    name = f'tile_tilemap--{tileset}_{index}'
    strata = strata

    surface = image
    surface = pygame.transform.rotate(surface, -orientation)
    
    rect = position

    return {
        'name': name,
        'surface': surface,

        'rect': pygame.Rect(rect[0], rect[1], *surface.get_size()),
        'dimensions': surface.get_size(),
        'orientation': orientation,
        
        'tileset': tileset,
        'index': index,
        
        'tile': tile,
        'strata': strata,
    }
