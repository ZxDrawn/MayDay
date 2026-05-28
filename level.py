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
        from assets import GLOBAL_OFFSETS
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset_x
        draw_rect.y += GLOBAL_OFFSETS.get('checkpoint', 0)
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
        from assets import GLOBAL_OFFSETS
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset_x
        draw_rect.y += GLOBAL_OFFSETS.get('beacon', 0)
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
    
    # Try to load custom level design from level_data.json first
    import json
    import os
    from assets import resource_path
    data_path = resource_path('Assets/level_data.json')
    if os.path.exists(data_path):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                
            # Load platforms
            for p_data in saved_data.get('platforms', []):
                platforms.add(Platform(p_data['x'], p_data['y'], p_data['width'], p_data['height']))
                
            # Load checkpoints
            for cp_data in saved_data.get('checkpoints', []):
                checkpoints.add(Checkpoint(cp_data['x'], cp_data['y'], cp_data['text_id'], cp_data['text_content']))
                
            # Load monkeys
            for m_data in saved_data.get('monkeys', []):
                monkeys.add(import_enemy("monkey", m_data['x'], m_data['y']))
                
            # Load birds
            for b_data in saved_data.get('birds', []):
                birds.add(import_enemy("bird", b_data['x'], b_data['y']))
                
            # Load beacon
            b_data = saved_data.get('beacon')
            if b_data:
                beacon = Beacon(b_data['x'], b_data['y'])
                
            # If successfully loaded, return!
            if len(platforms) > 0 and beacon is not None:
                # Ensure boundary left wall is present
                if not any(p.rect.x == -50 for p in platforms):
                    platforms.add(Platform(-50, 0, 50, 1000))
                return platforms, checkpoints, monkeys, birds, beacon
        except Exception as e:
            print(f"Warning: Failed to load level layout from JSON: {e}")
            platforms.empty()
            checkpoints.empty()
            monkeys.empty()
            birds.empty()
            beacon = None

    # 15km simulation (long level layout)
    
    # Start area
    platforms.add(Platform(0, 600, 800, 200))
    
    # Checkpoint 1
    checkpoints.add(Checkpoint(500, 472, 1, "Você ainda está vivo. Por enquanto."))
    
    # Section 1: Introduction to jumps and gaps
    platforms.add(Platform(920, 600, 400, 200))
    platforms.add(Platform(1400, 520, 300, 300))
    monkeys.add(import_enemy("monkey", 1500, 480))
    
    # Section 2: Climb
    platforms.add(Platform(1880, 420, 200, 400))
    platforms.add(Platform(2200, 290, 250, 500))
    birds.add(import_enemy("bird", 2300, 100))
    
    # Checkpoint 2
    checkpoints.add(Checkpoint(2250, 162, 2, "A selva ficou mais densa. Mas você ainda está de pé."))
    
    # Section 3: Longer gaps and multiple enemies
    platforms.add(Platform(2530, 410, 500, 400))
    monkeys.add(import_enemy("monkey", 2630, 370))
    monkeys.add(import_enemy("monkey", 2830, 370))
    
    platforms.add(Platform(3230, 480, 350, 300))
    birds.add(import_enemy("bird", 3350, 180))
    
    # Checkpoint 3
    platforms.add(Platform(3700, 580, 600, 200))
    checkpoints.add(Checkpoint(3900, 452, 3, "Metade do caminho. A segunda metade é pior."))
    
    # Section 4: Verticality and mix
    platforms.add(Platform(4400, 460, 200, 300))
    platforms.add(Platform(4700, 380, 200, 400))
    platforms.add(Platform(5020, 250, 200, 500))
    birds.add(import_enemy("bird", 4820, 100))
    monkeys.add(import_enemy("monkey", 5070, 210))
    
    platforms.add(Platform(5300, 560, 800, 200))
    
    # Checkpoint 4
    checkpoints.add(Checkpoint(5600, 432, 4, "Você pode ouvir eles. Eles já te ouviram faz tempo."))
    
    # Section 5: The final stretch
    platforms.add(Platform(6220, 480, 300, 300))
    monkeys.add(import_enemy("monkey", 6320, 440))
    
    platforms.add(Platform(6660, 380, 300, 400))
    birds.add(import_enemy("bird", 6810, 100))
    
    platforms.add(Platform(7100, 250, 300, 500))
    monkeys.add(import_enemy("monkey", 7200, 210))
    
    # Final Platform (Beacon Area)
    platforms.add(Platform(7620, 380, 600, 400))
    
    # The Beacon
    beacon = Beacon(8020, 260)
    
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
