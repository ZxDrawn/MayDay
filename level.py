import pygame
from settings import *
from assets import IMAGES

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=COLOR_PLATFORM):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        # Top dark green border to simulate a grass layer on the platforms
        pygame.draw.rect(self.image, (46, 117, 89), (0, 0, width, 6))

    def draw(self, surface, camera_offset_x):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset_x
        surface.blit(self.image, draw_rect)

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y, text_id, text_content):
        super().__init__()
        self.rect = pygame.Rect(x, y, 64, 128)
        self.text_id = text_id
        self.text_content = text_content
        self.active = False
        
    def draw(self, surface, camera_offset_x):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset_x
        # Sit exactly on the ground, no sinking
        surface.blit(IMAGES['checkpoint'], draw_rect)
        
        # pulsating active indicator light
        if self.active:
            light_color = (100, 255, 100) # Green for active
        else:
            light_color = (255, 50, 50) # Red for inactive
            
        light_radius = 5 + math.sin(pygame.time.get_ticks() * 0.01) * 2
        # draw at top of checkpoint pole
        pygame.draw.circle(surface, light_color, (draw_rect.x + 32, draw_rect.y + 15), int(light_radius))
        
        # Draw subtle aura
        surf_aura = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(surf_aura, (*light_color, 40), (15, 15), int(light_radius * 2))
        surface.blit(surf_aura, (draw_rect.x + 32 - 15, draw_rect.y + 15 - 15))

class Beacon(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 80, 120)
        
    def draw(self, surface, camera_offset_x):
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset_x
        # Sit exactly on the ground, no sinking
        surface.blit(IMAGES['beacon'], draw_rect)
        
        # pulsating light
        light_radius = 18 + math.sin(pygame.time.get_ticks() * 0.005) * 5
        # Glowing center
        pygame.draw.circle(surface, (255, 100, 100), (draw_rect.centerx, draw_rect.top + 30), int(light_radius))
        # Semi-transparent red glowing aura
        surf_aura = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(surf_aura, (255, 50, 50, 45), (50, 50), int(light_radius * 1.8))
        surface.blit(surf_aura, (draw_rect.centerx - 50, draw_rect.top + 30 - 50))

import math

def generate_level():
    platforms = pygame.sprite.Group()
    checkpoints = pygame.sprite.Group()
    monkeys = pygame.sprite.Group()
    birds = pygame.sprite.Group()
    beacon = None
    
    # 15km simulation (long level layout)
    
    # Start area
    platforms.add(Platform(0, 600, 800, 200))
    
    # Checkpoint 1
    checkpoints.add(Checkpoint(500, 472, 1, "Você ainda está vivo. Por enquanto."))
    
    # Section 1: Introduction to jumps and gaps
    platforms.add(Platform(920, 600, 400, 200))
    platforms.add(Platform(1440, 500, 300, 300))
    monkeys.add(import_enemy("monkey", 1540, 460))
    
    # Section 2: Climb
    platforms.add(Platform(1860, 400, 200, 400))
    platforms.add(Platform(2180, 300, 200, 500))
    birds.add(import_enemy("bird", 2280, 100))
    
    # Checkpoint 2
    checkpoints.add(Checkpoint(2230, 172, 2, "A selva ficou mais densa. Mas você ainda está de pé."))
    
    # Section 3: Longer gaps and multiple enemies
    platforms.add(Platform(2500, 400, 500, 400))
    monkeys.add(import_enemy("monkey", 2600, 360))
    monkeys.add(import_enemy("monkey", 2800, 360))
    
    platforms.add(Platform(3120, 500, 400, 300))
    birds.add(import_enemy("bird", 3320, 200))
    
    # Checkpoint 3
    platforms.add(Platform(3640, 600, 600, 200))
    checkpoints.add(Checkpoint(3840, 472, 3, "Metade do caminho. A segunda metade é pior."))
    
    # Section 4: Verticality and mix
    platforms.add(Platform(4360, 500, 200, 300))
    platforms.add(Platform(4680, 400, 200, 400))
    platforms.add(Platform(5000, 300, 200, 500))
    birds.add(import_enemy("bird", 4800, 150))
    monkeys.add(import_enemy("monkey", 5050, 260))
    
    platforms.add(Platform(5320, 600, 800, 200))
    
    # Checkpoint 4
    checkpoints.add(Checkpoint(5620, 472, 4, "Você pode ouvir eles. Eles já te ouviram faz tempo."))
    
    # Section 5: The final stretch
    platforms.add(Platform(6240, 500, 300, 300))
    monkeys.add(import_enemy("monkey", 6340, 460))
    
    platforms.add(Platform(6660, 400, 300, 400))
    birds.add(import_enemy("bird", 6810, 100))
    
    platforms.add(Platform(7080, 300, 300, 500))
    monkeys.add(import_enemy("monkey", 7180, 260))
    
    # Final Checkpoint
    platforms.add(Platform(7500, 400, 600, 400))
    checkpoints.add(Checkpoint(7600, 272, 5, "O sinalizador está perto. Não deixe a Terra saber disso."))
    
    # The Beacon
    beacon = Beacon(7900, 280)
    
    # Add bounds
    platforms.add(Platform(-50, 0, 50, 1000)) # Left wall

    return platforms, checkpoints, monkeys, birds, beacon

def import_enemy(enemy_type, x, y):
    # dynamic import to avoid circular dependency
    import entities
    if enemy_type == "monkey":
        return entities.Monkey(x, y)
    elif enemy_type == "bird":
        return entities.Bird(x, y)
