import pygame
import sys
from settings import *
from entities import Player
from level import generate_level
from ui import UI
from assets import load_assets, IMAGES

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("MAYDAY")
    
    # Load all image assets now that display is initialized
    load_assets()
    
    clock = pygame.time.Clock()

    state = "MENU" # MENU, STORY, PLAYING, GAME_OVER, VICTORY
    ui = UI()

    player = None
    platforms = None
    checkpoints = None
    monkeys = None
    birds = None
    beacon = None
    
    respawn_pos = (100, 400)
    camera_offset_x = 0

    def start_game(load_from_checkpoint=False):
        nonlocal player, platforms, checkpoints, monkeys, birds, beacon, respawn_pos, camera_offset_x
        if not load_from_checkpoint:
            respawn_pos = (100, 400)
            
        platforms, checkpoints, monkeys, birds, beacon = generate_level()
        player = Player(*respawn_pos)
        
        # Adjust camera immediately
        camera_offset_x = player.rect.centerx - WINDOW_WIDTH // 2

    while True:
        dt = clock.tick(FPS)
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "MENU":
                    clicked = ui.get_menu_click(mouse_pos)
                    if clicked == "INICIAR MISSÃO":
                        state = "STORY"
                    elif clicked and "MODO DEV" in clicked:
                        import settings
                        settings.DEV_MODE = not settings.DEV_MODE
                    elif clicked == "SAIR":
                        pygame.quit()
                        sys.exit()
                elif state == "STORY":
                    start_game()
                    state = "PLAYING"
                elif state == "GAME_OVER":
                    clicked = ui.get_game_over_click(mouse_pos)
                    if clicked == "TENTAR NOVAMENTE":
                        start_game(load_from_checkpoint=True)
                        state = "PLAYING"
                    elif clicked == "VOLTAR AO MENU":
                        state = "MENU"
                elif state == "VICTORY":
                    if hasattr(ui, 'vic_rect') and ui.vic_rect.collidepoint(mouse_pos):
                        state = "MENU"

            if event.type == pygame.KEYDOWN:
                if state == "STORY" and event.key == pygame.K_SPACE:
                    start_game()
                    state = "PLAYING"
                # Quick respawn from checkpoint for testing/gameplay
                if state == "GAME_OVER" and event.key == pygame.K_r:
                    start_game(load_from_checkpoint=True)
                    state = "PLAYING"

        # State updates & rendering
        if state == "MENU":
            ui.draw_menu(screen)
            
        elif state == "STORY":
            ui.draw_story(screen)
            
        elif state == "PLAYING":
            # Update entities
            enemies = pygame.sprite.Group()
            enemies.add(*monkeys)
            enemies.add(*birds)
            
            player.update(keys, mouse_buttons, platforms, enemies)
            
            for m in monkeys:
                m.update(player, platforms)
            for b in birds:
                b.update(player, platforms)

            # Camera logic
            target_camera_x = player.rect.centerx - WINDOW_WIDTH // 2
            # Simple lerp for smooth camera
            camera_offset_x += (target_camera_x - camera_offset_x) * 0.1
            
            # Don't let camera go left of level start
            if camera_offset_x < 0:
                camera_offset_x = 0

            # Checkpoints
            for cp in checkpoints:
                if not cp.active and player.rect.colliderect(cp.rect):
                    cp.active = True
                    respawn_pos = (cp.rect.x, cp.rect.y - 60)
                    ui.show_lore(cp.text_content)
                    
            # Beacon collision
            if player.rect.colliderect(beacon.rect):
                state = "VICTORY"

            # Death
            if player.is_dead:
                state = "GAME_OVER"

            # Rendering
            screen.blit(IMAGES['bg'], (0, 0))
            
            # Draw platforms
            for p in platforms:
                p.draw(screen, camera_offset_x)
                
            for cp in checkpoints:
                cp.draw(screen, camera_offset_x)
                
            beacon.draw(screen, camera_offset_x)
                
            for m in monkeys:
                m.draw(screen, camera_offset_x)
                
            for b in birds:
                b.draw(screen, camera_offset_x)
                
            player.draw(screen, camera_offset_x)
            
            ui.draw_hud(screen, player)

        elif state == "GAME_OVER":
            ui.draw_game_over(screen)
            
        elif state == "VICTORY":
            ui.draw_victory(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main()
