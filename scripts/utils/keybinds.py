import pygame

class Keybinds:
    KEYBINDS = {
        'clear_selected': [pygame.K_ESCAPE],

        'rotate': [pygame.K_r],
        'flip': [pygame.K_f],

        'toggle_placing': [pygame.K_t],
        'toggle_strata_alpha': [pygame.K_y],

        'strata_up': [pygame.K_e],
        'strata_down': [pygame.K_q],

        'select_section': [pygame.K_g],
        'select_move_x': [pygame.K_z],
        'select_move_y': [pygame.K_x]
    }