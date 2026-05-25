import pygame
import sys
import os
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

IMAGES = {}

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_assets():
    # Background
    bg_path = resource_path('Assets/Background.png')
    if os.path.exists(bg_path):
        bg_img = pygame.transform.scale(pygame.image.load(bg_path).convert(), (WINDOW_WIDTH, WINDOW_HEIGHT))
        # Create a vertical gradient mask to dim the background and highlight the player/enemies
        gradient = pygame.Surface((1, WINDOW_HEIGHT), pygame.SRCALPHA)
        for y in range(WINDOW_HEIGHT):
            # Alpha goes from 210 at the top (very dark) to 120 at the bottom (moderately dark)
            alpha = int(215 - (y / WINDOW_HEIGHT) * 95)
            gradient.set_at((0, y), (10, 10, 18, alpha)) # Dark blue-black night filter
        gradient_scaled = pygame.transform.scale(gradient, (WINDOW_WIDTH, WINDOW_HEIGHT))
        bg_img.blit(gradient_scaled, (0, 0))
        IMAGES['bg'] = bg_img
    else:
        # Fallback
        surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        surf.fill((10, 10, 18))
        IMAGES['bg'] = surf
        
    # Floor
    floor_path = resource_path('Assets/Movimentação/floor.png')
    if os.path.exists(floor_path):
        IMAGES['floor'] = pygame.image.load(floor_path).convert_alpha()
    else:
        surf = pygame.Surface((64, 64))
        surf.fill((101, 67, 33)) # Earth brown color
        IMAGES['floor'] = surf

    # Player states (Sgt. Kael Voss)
    player_size = (40, 60)
    def load_player_img(filename):
        path = resource_path(f'Assets/Movimentação/kael_Voss_anim/{filename}')
        if os.path.exists(path):
            return pygame.transform.scale(pygame.image.load(path).convert_alpha(), player_size)
        else:
            surf = pygame.Surface(player_size)
            surf.fill((42, 157, 143))
            return surf

    IMAGES['player_stand'] = load_player_img('stand.png')
    IMAGES['player_walk_1'] = load_player_img('walk_1.png')
    IMAGES['player_walk_2'] = load_player_img('walk_2.png')
    IMAGES['player_normal_attack'] = load_player_img('normal_atack.png')
    IMAGES['player_strong_attack'] = load_player_img('strong_atack.png')

    # Monkey states
    def load_monkey_img(filename, size=(50, 50)):
        path = resource_path(f'Assets/Movimentação/macaco_anim/{filename}')
        if os.path.exists(path):
            return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
        else:
            surf = pygame.Surface(size)
            surf.fill((230, 57, 70))
            return surf

    IMAGES['monkey_stand'] = load_monkey_img('Macaco_stopped.png', (54, 54))
    IMAGES['monkey_walk_1'] = load_monkey_img('Macaco_walk_1.png', (50, 50))
    IMAGES['monkey_walk_2'] = load_monkey_img('Macaco_walk_2.png', (50, 50))
    IMAGES['monkey_attack'] = load_monkey_img('Macaco_attack.png', (54, 54))

    # Bird states
    bird_size = (40, 40) # slightly bigger to fit the generated bird sprite well
    def load_bird_img(filename):
        path = resource_path(f'Assets/Movimentação/bird_anim/{filename}')
        if os.path.exists(path):
            return pygame.transform.scale(pygame.image.load(path).convert_alpha(), bird_size)
        else:
            surf = pygame.Surface(bird_size)
            surf.fill((241, 135, 1) if filename == 'bird_fly_1.png' else (241, 160, 50))
            return surf

    IMAGES['bird_fly_1'] = load_bird_img('bird_fly_1.png')
    IMAGES['bird_fly_2'] = load_bird_img('bird_fly_2.png')

    # Checkpoint
    checkpoint_path = resource_path('Assets/checkpoint.png')
    checkpoint_size = (64, 128)
    if os.path.exists(checkpoint_path):
        IMAGES['checkpoint'] = pygame.transform.scale(pygame.image.load(checkpoint_path).convert_alpha(), checkpoint_size)
    else:
        # Fallback
        surf = pygame.Surface(checkpoint_size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (100, 100, 100), (28, 0, 8, 128)) # pole
        pygame.draw.rect(surf, (200, 50, 50), (0, 0, 32, 24)) # flag
        IMAGES['checkpoint'] = surf

    # Beacon
    beacon_path = resource_path('Assets/beacon.png')
    beacon_size = (80, 120)
    if os.path.exists(beacon_path):
        IMAGES['beacon'] = pygame.transform.scale(pygame.image.load(beacon_path).convert_alpha(), beacon_size)
    else:
        surf = pygame.Surface(beacon_size)
        surf.fill((50, 50, 80))
        IMAGES['beacon'] = surf
