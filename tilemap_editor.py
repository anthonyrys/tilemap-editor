class TilemapEditor:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock

        self.fullscreen = False

        self.tilemap_path = None
        self.tilemap = None

        self.components = {
            'sidebar': prefabs.sidebar(),
            'tilemap': None,
            'tiles': []
        }

        self.mouse = {
            'hovers': [],

            'press': False,
            'press_position': [[0, 0], [0, 0]]
        }

        self.display_data = {
            'interface_images': {},
            'position': [],

            'offset': [0, 0],
            'current_offset': [0, 0],

            'strata': 1,
            'orientation': 0
        }

        self.interface_tile = None

    def register_pygame_events(self):
        quit = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_tilemap()
                quit = True

            elif event.type == pygame.KEYDOWN:
                if event.key in utils.Keybinds.KEYBINDS['clear_selected']:
                    self.interface_tile = None
                
                elif event.key in utils.Keybinds.KEYBINDS['rotate']:
                    self.display_data['orientation'] += 90
                    if self.display_data['orientation'] == 360:
                        self.display_data['orientation'] = 0

                elif event.key in utils.Keybinds.KEYBINDS['strata_up']:
                    self.display_data['strata'] += 1
                    if self.display_data['strata'] == 10:
                        self.display_data['strata'] = 0

                elif event.key in utils.Keybinds.KEYBINDS['strata_down']:
                    self.display_data['strata'] -= 1
                    if self.display_data['strata'] == -1:
                        self.display_data['strata'] = 9


                if event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                    if self.tilemap:
                        self.save_tilemap()
  
                elif event.key == pygame.K_l and event.mod & pygame.KMOD_CTRL:
                    self.load_tilemap(filedialog.askdirectory())

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.on_mouse_down(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.on_mouse_up(event)

        return quit
    
    def register_mouse_events(self):
        position = pygame.mouse.get_pos()

        for component in self.components.values():
            if not isinstance(component, list):
                component = [component]

            for v in component:
                if not v:
                    continue

                if not v['rect'].collidepoint(position):
                    if v in self.mouse['hovers']:
                        self.mouse['hovers'].remove(v)

                    continue

                if v not in self.mouse['hovers']:
                    self.mouse['hovers'].append(v)

        for image in self.display_data['interface_images']:
            for surface in self.display_data['interface_images'][image]:

                if not surface['rect'].collidepoint(position):
                    if surface in self.mouse['hovers']:
                        self.mouse['hovers'].remove(surface)

                    continue

                if surface not in self.mouse['hovers']:
                    self.mouse['hovers'].append(surface)

        buttons = pygame.mouse.get_pressed()
        if buttons[0]:
            if not self.components['tilemap'] or self.components['tilemap'] not in self.mouse['hovers']:
                return
            
            if not self.interface_tile:
                return

            interface_tile = self.interface_tile

            tile = prefabs.tile_tilemap(
                self.display_data['position_grid'],
                interface_tile['surface'],
                self.display_data['orientation'],
                interface_tile['tileset'],
                interface_tile['index'],
                interface_tile['tile'],
                self.display_data['strata']
            )

            for v in self.components['tiles']:
                if v['rect'] == tile['rect']:
                    self.components['tiles'].remove(v)

            self.components['tiles'].append(tile)

        elif buttons[1]:
            ...

        elif buttons[2]:
            if not self.components['tilemap'] or self.components['tilemap'] not in self.mouse['hovers']:
                return

            for tile in [t for t in self.components['tiles'] if t['rect'].collidepoint(self.display_data['position_grid'])]:
                self.components['tiles'].remove(tile)

    def on_mouse_down(self, event):
        if event.button == 1:
            if not self.interface_tile:
                self.mouse['press'] = True
                self.mouse['press_position'][0] = pygame.mouse.get_pos()

    def on_mouse_up(self, event):
        if event.button == 1:
            for interface_tile in [c for c in self.mouse['hovers'] if c['name'].split('--')[0] == 'tile_interface']:
                self.interface_tile = interface_tile

            x_offset = self.mouse['press_position'][1][0] - self.mouse['press_position'][0][0]
            y_offset = self.mouse['press_position'][1][1] - self.mouse['press_position'][0][1]

            self.display_data['offset'][0] += x_offset
            self.display_data['offset'][1] += y_offset

            self.mouse['press'] = False
            self.mouse['press_position'] = [[0, 0], [0, 0]]
            
        elif event.button == 2:
            ...
        
        elif event.button == 3:
            ...

    def save_tilemap(self):
        self.interface_tile = None

        self.tilemap['tiles'] = []
        for tile in self.components['tiles']:
            self.tilemap['tiles'].append(
                {
                    'position': [tile['rect'].x, tile['rect'].y],
                    'dimensions': [tile['rect'].width, tile['rect'].height],
                    'orientation': tile['orientation'],

                    'tileset': tile['tileset'],
                    'index': tile['index'],

                    'tile': tile['tile'],
                    'strata': tile['strata']
                }
            )

        services.save(self.tilemap, self.tilemap_path)

    def load_tilemap(self, path):
        if self.tilemap:
            self.save_tilemap()
            
        self.components = {
            'sidebar': prefabs.sidebar(),
            'tilemap': None,
            'tiles': []
        }

        self.mouse = {
            'hovers': [],

            'press': False,
            'press_position': [[0, 0], [0, 0]]
        }

        self.display_data = {
            'interface_images': {},
            'position': [],

            'offset': [0, 0],
            'current_offset': [0, 0],

            'strata': 1,
            'orientation': 0
        }

        self.interface_tile = None

        self.tilemap = services.load(path)
        if not self.tilemap:
            return
        
        self.tilemap_path = path
        
        x, y = 0, 0
        padding = [8, 8]
        for image in self.tilemap['config']['images']:
            self.display_data['interface_images'][image] = []

            spritesheet_path = os.path.join(path, self.tilemap['config']['images'][image]['path'])
            for i, surface in enumerate(services.load_spritesheet(spritesheet_path, 2)):
                tile = self.tilemap['config']['images'][image]['tiles']
                if isinstance(tile, list):
                    tile = tile[i]
                
                position = [
                    padding[0] + ((padding[0] + surface.get_width()) * x),
                    padding[1] + ((padding[1] + surface.get_height()) * y),
                ]

                prefab = prefabs.tile_interface(position, surface, 0, image, i, tile, 1)

                self.display_data['interface_images'][image].append(prefab)

                x += 1
                if x > 3:
                    x = 0
                    y += 1

        dimensions = [
            self.tilemap['config']['tile']['dimensions'][0] * self.tilemap['config']['tilemap']['dimensions'][0],
            self.tilemap['config']['tile']['dimensions'][1] * self.tilemap['config']['tilemap']['dimensions'][1]
        ]

        self.components['tilemap'] = prefabs.tilemap_surface(dimensions)

        for t in self.tilemap['tiles']:
            tile = self.tilemap['config']['images'][t['tileset']]['tiles']
            if isinstance(tile, list):
                tile = tile[t['index']]

            tile = prefabs.tile_tilemap(
                t['position'],
                self.display_data['interface_images'][t['tileset']][t['index']]['surface'].copy(),
                t['orientation'],
                t['tileset'],
                t['index'],
                tile,
                t['strata']
            )

            self.components['tiles'].append(tile)

    def update_tilemap_surface(self):
        tilemap_surface = self.components['tilemap']
        tilemap_surface['surface'].fill(tilemap_surface['color'])
            
        offset = self.display_data['current_offset']

        mouse_position = [*pygame.mouse.get_pos()]

        mouse_position[0] -= tilemap_surface['rect'].x + offset[0]
        mouse_position[1] -= tilemap_surface['rect'].y + offset[1]

        tile_dimensions = self.tilemap['config']['tile']['dimensions']
        position = [
            (tile_dimensions[0] * round(mouse_position[0] / tile_dimensions[0])),
            (tile_dimensions[1] * round(mouse_position[1] / tile_dimensions[1])),
        ]

        self.display_data['position_free'] = mouse_position
        self.display_data['position_grid'] = position

        if self.interface_tile:
            surf = self.interface_tile['surface'].copy()
            surf = pygame.transform.rotate(surf, -self.display_data['orientation'])
            surf.set_alpha(100)

            tilemap_surface['surface'].blit(surf, self.display_data['position_grid'])

        for tile in self.components['tiles']:
            tilemap_surface['surface'].blit(tile['surface'], tile['rect'])

        screen.blit(tilemap_surface['surface'], 
                [tilemap_surface['rect'][0] + self.display_data['current_offset'][0], 
                tilemap_surface['rect'][1] + self.display_data['current_offset'][1]])

    def update(self):
        if not self.tilemap:
            pygame.display.set_caption(f'{TITLE} | fps: {round(clock.get_fps(), 1)}')
        else:
            pygame.display.set_caption(f'{self.tilemap["config"]["name"]} | fps: {round(clock.get_fps(), 1)}')

        quit = self.register_pygame_events()
        self.register_mouse_events()

        if self.mouse['press']:
            self.mouse['press_position'][1] = pygame.mouse.get_pos()
        
        x_offset = self.mouse['press_position'][1][0] - self.mouse['press_position'][0][0]
        y_offset = self.mouse['press_position'][1][1] - self.mouse['press_position'][0][1]

        current_offset = [
            self.display_data['offset'][0] + x_offset,
            self.display_data['offset'][1] + y_offset
        ]

        self.display_data['current_offset'] = current_offset

        if self.display_data['offset'][0] > 0:
            self.display_data['offset'][0] = 0
        if self.display_data['offset'][1] > 0:
            self.display_data['offset'][1] = 1

        if self.components['tilemap']:
            self.update_tilemap_surface()

        self.components['sidebar']['surface'].fill(self.components['sidebar']['color'])
        for image in self.display_data['interface_images']:
            for surface in self.display_data['interface_images'][image]:
                if surface == self.interface_tile:
                    outline = pygame.Surface((surface['rect'].width * 1.1, surface['rect'].height * 1.1))
                    outline.fill((255, 255, 255))
                    
                    self.components['sidebar']['surface'].blit(outline, outline.get_rect(center=surface['rect'].center))

                self.components['sidebar']['surface'].blit(surface['surface'], surface['rect'])

        screen.blit(self.components['sidebar']['surface'], self.components['sidebar']['rect'])

        return quit

if __name__ == '__main__':
    from scripts import (
        TITLE, SCREEN_COLOR, FRAME_RATE, 
        SCREEN_DIMENSIONS, SCREEN_COLOR
    )

    import scripts.prefabs as prefabs
    import scripts.services as services
    import scripts.utils as utils

    import pygame
    import tkinter
    import sys
    import os

    from tkinter import filedialog

    tkinter.Tk().withdraw()
    pygame.init()

    screen = pygame.display.set_mode(SCREEN_DIMENSIONS)
    clock = pygame.time.Clock()

    tilemap_editor = TilemapEditor(screen, clock)

    quit = False
    while not quit: 
        screen.fill(SCREEN_COLOR)
        quit = tilemap_editor.update()

        pygame.display.flip()

        clock.tick(FRAME_RATE)

    pygame.quit()
    sys.exit()