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

            'grid_placing': True,

            'offset': [0, 0],
            'current_offset': [0, 0],

            'strata': 0,
            'orientation': 0,
            'flipped': False,

            'strata_alpha': False
        }

        self.interface_tile = None

        self.selecting = False
        self.selected_tiles = []
        self.selecting_pos = [0, 0]
        self.selecting_rect = None

    def register_pygame_events(self):
        quit = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_tilemap()
                quit = True

            elif event.type == pygame.KEYDOWN:
                if event.key in utils.Keybinds.KEYBINDS['clear_selected']:
                    self.interface_tile = None
                    self.selected_tiles = []
                
                elif event.key in utils.Keybinds.KEYBINDS['rotate']:
                    self.display_data['orientation'] += 90
                    if self.display_data['orientation'] == 360:
                        self.display_data['orientation'] = 0

                elif event.key in utils.Keybinds.KEYBINDS['flip']:
                    self.display_data['flipped'] = not self.display_data['flipped'] 

                elif event.key in utils.Keybinds.KEYBINDS['strata_up']:
                    self.display_data['strata'] += 1
                    if self.display_data['strata'] == 10:
                        self.display_data['strata'] = 0

                elif event.key in utils.Keybinds.KEYBINDS['strata_down']:
                    self.display_data['strata'] -= 1
                    if self.display_data['strata'] == -1:
                        self.display_data['strata'] = 9

                elif event.key in utils.Keybinds.KEYBINDS['toggle_strata_alpha']:
                    self.display_data['strata_alpha'] = not self.display_data['strata_alpha']

                elif event.key in utils.Keybinds.KEYBINDS['toggle_placing']:
                    self.display_data['grid_placing'] = not self.display_data['grid_placing']

                elif event.key in utils.Keybinds.KEYBINDS['select_section']:
                    if self.components['tilemap']:
                        tilemap_surface = self.components['tilemap']
                        offset = self.display_data['current_offset']

                        mouse_position = [*pygame.mouse.get_pos()]
                        mouse_position[0] -= tilemap_surface['rect'].x + offset[0]
                        mouse_position[1] -= tilemap_surface['rect'].y + offset[1]
                        
                        self.selecting = True
                        self.selecting_pos = mouse_position

                elif event.key in utils.Keybinds.KEYBINDS['select_move_x']:
                    if self.tilemap:
                        if self.display_data['grid_placing']:
                            per_pos = self.tilemap['config']['tile']['dimensions'][0]
                        else:
                            per_pos = self.tilemap['config']['tile']['dimensions'][0] // 4

                        if event.mod & pygame.KMOD_SHIFT:
                            per_pos = -per_pos

                        for tile in self.selected_tiles:
                            if tile['rect'].x + per_pos < 0:
                                continue

                            if tile['rect'].x + per_pos > self.components['tilemap']['surface'].get_width():
                                continue

                            self.components['tiles'][self.components['tiles'].index(tile)]['rect'].x += per_pos 

                elif event.key in utils.Keybinds.KEYBINDS['select_move_y']:
                    if self.tilemap:
                        if self.display_data['grid_placing']:
                            per_pos = self.tilemap['config']['tile']['dimensions'][1]
                        else:
                            per_pos = self.tilemap['config']['tile']['dimensions'][1] // 4
                    
                        if event.mod & pygame.KMOD_SHIFT:
                            per_pos = -per_pos

                        for tile in self.selected_tiles:
                            if tile['rect'].y + per_pos < 0:
                                continue

                            if tile['rect'].y + per_pos > self.components['tilemap']['surface'].get_height():
                                continue

                            self.components['tiles'][self.components['tiles'].index(tile)]['rect'].y += per_pos

                if event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                    if self.tilemap:
                        self.save_tilemap()
  
                elif event.key == pygame.K_l and event.mod & pygame.KMOD_CTRL:
                    self.load_tilemap(filedialog.askdirectory())

            elif event.type == pygame.KEYUP:
                if event.key in utils.Keybinds.KEYBINDS['select_section']:
                    self.selecting = False
                    self.selected_tiles = []

                    for tile in self.components['tiles']:
                        if tile['rect'].colliderect(self.selecting_rect) and self.display_data['strata'] == tile['strata']:
                            self.selected_tiles.append(tile)
                    
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
                self.display_data['position'],
                interface_tile['surface'],
                self.display_data['orientation'],
                self.display_data['flipped'],
                interface_tile['tileset'],
                interface_tile['index'],
                interface_tile['tile'],
                self.display_data['strata']
            )

            for v in self.components['tiles']:
                if v['rect'] == tile['rect'] and v['strata'] == tile['strata']:
                    self.components['tiles'].remove(v)

            self.components['tiles'].append(tile)

        elif buttons[1]:
            ...

        elif buttons[2]:
            if not self.components['tilemap'] or self.components['tilemap'] not in self.mouse['hovers']:
                return

            for tile in [t for t in self.components['tiles'] 
                            if t['rect'].collidepoint(self.display_data['position'])
                            and t['strata'] == self.display_data['strata']]:
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

        if not self.tilemap:
            return
        
        self.tilemap['config']['offset'] = self.display_data['current_offset']
        self.tilemap['config']['strata_alpha'] = self.display_data['strata_alpha']
        self.tilemap['config']['grid_placing'] = self.display_data['grid_placing']

        self.tilemap['config']['strata'] = self.display_data['strata']
        self.tilemap['config']['orientation'] = self.display_data['orientation']
        self.tilemap['config']['flipped'] = self.display_data['flipped']

        self.tilemap['tiles'] = []
        for tile in self.components['tiles']:
            self.tilemap['tiles'].append(
                {
                    'position': [tile['rect'].x, tile['rect'].y],
                    'dimensions': [tile['rect'].width, tile['rect'].height],
                    'orientation': tile['orientation'],
                    'flipped': tile['flipped'],

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

            'grid_placing': True,

            'offset': [0, 0],
            'current_offset': [0, 0],

            'strata': 0,
            'orientation': 0,
            'flipped': False,

            'strata_alpha': False
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
                    padding[0] + ((padding[0] + self.tilemap['config']['tile']['dimensions'][0]) * x),
                    padding[1] + ((padding[1] + self.tilemap['config']['tile']['dimensions'][1]) * y),
                ]

                prefab = prefabs.tile_interface(position, surface, 0, False, image, i, tile, 1)

                self.display_data['interface_images'][image].append(prefab)

                x += 1
                if x > 3:
                    x = 0
                    y += 1

        dimensions = [
            self.tilemap['config']['tile']['dimensions'][0] * self.tilemap['config']['tilemap']['dimensions'][0],
            self.tilemap['config']['tile']['dimensions'][1] * self.tilemap['config']['tilemap']['dimensions'][1]
        ]
        
        self.display_data['current_offset'] = self.tilemap['config']['offset']
        self.display_data['offset'] = self.tilemap['config']['offset']

        self.display_data['strata_alpha'] = self.tilemap['config']['strata_alpha']
        self.display_data['grid_placing'] = self.tilemap['config']['grid_placing']

        self.display_data['strata'] = self.tilemap['config']['strata']
        self.display_data['orientation'] = self.tilemap['config']['orientation']
        self.display_data['flipped'] = self.tilemap['config']['flipped']

        self.components['tilemap'] = prefabs.tilemap_surface(dimensions)

        for t in self.tilemap['tiles']:
            try:
                tile = self.tilemap['config']['images'][t['tileset']]['tiles']
                if isinstance(tile, list):
                    tile = tile[t['index']]

                tile = prefabs.tile_tilemap(
                    t['position'],
                    self.display_data['interface_images'][t['tileset']][t['index']]['surface'].copy(),
                    t['orientation'],
                    t['flipped'],
                    t['tileset'],
                    t['index'],
                    tile,
                    t['strata']
                )

                self.components['tiles'].append(tile)

            except (IndexError) as e:
                print(e)
                continue

        pygame.display.set_caption(f'{self.tilemap["config"]["name"]}')

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

        if self.display_data['grid_placing']:
            self.display_data['position'] = position
        else:
            self.display_data['position'] = mouse_position

        display_rect = pygame.Rect(
            -self.display_data['current_offset'][0],
            -self.display_data['current_offset'][1],
            *SCREEN_DIMENSIONS
        )

        if self.selecting:
            position = [0, 0]
            size = [
                abs(self.display_data['position'][0] - self.selecting_pos[0]),
                abs(self.display_data['position'][1] - self.selecting_pos[1])
            ]

            if self.display_data['position'][0] <= self.selecting_pos[0]:
                position[0] = self.display_data['position'][0]
            else:
                position[0] = self.selecting_pos[0]

            if self.display_data['position'][1] <= self.selecting_pos[1]:
                position[1] = self.display_data['position'][1]
            else:
                position[1] = self.selecting_pos[1]

            self.selecting_rect = pygame.Rect(*position, *size)
            pygame.draw.rect(tilemap_surface['surface'], (255, 0, 0), self.selecting_rect)

        for tile in self.selected_tiles:
            outline = pygame.Surface((tile['rect'].width * 1.1, tile['rect'].height * 1.1))
            outline.fill((255, 0, 0))

            tilemap_surface['surface'].blit(outline, outline.get_rect(center=tile['rect'].center))

        drawable_tiles = [t for t in self.components['tiles'] if display_rect.colliderect(t['rect'])]

        if self.display_data['strata_alpha']:
            for tile in sorted([t for t in drawable_tiles if t['strata'] != self.display_data['strata']], key = lambda t: t['strata']):
                surf = tile['surface'].copy()
                surf.set_alpha(100)

                tilemap_surface['surface'].blit(surf, tile['rect'])

            for tile in [t for t in drawable_tiles if t['strata'] == self.display_data['strata']]:
                tilemap_surface['surface'].blit(tile['surface'], tile['rect'])

        else:
            for tile in sorted(drawable_tiles, key = lambda t: t['strata']):
                tilemap_surface['surface'].blit(tile['surface'], tile['rect'])

        if self.interface_tile:
            surf = self.interface_tile['surface'].copy()
            surf = pygame.transform.rotate(surf, -self.display_data['orientation'])
            surf = pygame.transform.flip(surf, self.display_data['flipped'], False)

            tilemap_surface['surface'].blit(surf, self.display_data['position'])

        screen.blit(tilemap_surface['surface'], 
                [tilemap_surface['rect'][0] + self.display_data['current_offset'][0], 
                tilemap_surface['rect'][1] + self.display_data['current_offset'][1]])

        x, y = self.display_data['position']
        if self.display_data['grid_placing']:
            position_surface = utils.create_text(f'position (grid): {x}, {y}')
        else:
            position_surface = utils.create_text(f'position (free): {x}, {y}')

        strata_surface = utils.create_text(f'strata: {self.display_data["strata"]}')
        orientation_surface = utils.create_text(f'orientation: {self.display_data["orientation"]}')
        flipped_surface = utils.create_text(f'flipped: {self.display_data["flipped"]}')

        screen.blit(position_surface, (325, 750))
        screen.blit(orientation_surface, (325, 715))
        screen.blit(flipped_surface, (325, 680))
        screen.blit(strata_surface, (325, 645))

        if self.interface_tile:
            tileset_tile = self.tilemap['config']['images'][self.interface_tile['tileset']]['tiles']
            if isinstance(tileset_tile, list):
                tileset_tile = tileset_tile[self.interface_tile['index']]
            tileset_tile = tileset_tile.replace('_', ' ')

            tile_surface = utils.create_text(f'tile: {tileset_tile}')
            screen.blit(tile_surface, (325, 610))

    def update(self):
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

        fps_surface = utils.create_text(str(round(clock.get_fps())))
        screen.blit(fps_surface, fps_surface.get_rect(topright=[SCREEN_DIMENSIONS[0] - 5, 5]))

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

    pygame.display.set_caption(f'{TITLE}')

    utils.Fonts.init()

    tilemap_editor = TilemapEditor(screen, clock)

    quit = False
    while not quit: 
        screen.fill(SCREEN_COLOR)
        quit = tilemap_editor.update()

        pygame.display.flip()

        clock.tick(FRAME_RATE)

    pygame.quit()
    sys.exit()
