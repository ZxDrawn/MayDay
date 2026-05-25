import pygame
import sys
from settings import *
from entities import Player
from level import generate_level
from ui import UI
from assets import load_assets, IMAGES, SOUNDS, play_bgm, stop_bgm

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

    # Editor State variables
    selected_entity = None
    selected_type = None # "Player", "Platform", "Checkpoint", "Monkey", "Bird", "Beacon"
    dragging = False
    drag_offset_x = 0
    drag_offset_y = 0
    save_success_timer = 0

    def start_game(load_from_checkpoint=False):
        nonlocal player, platforms, checkpoints, monkeys, birds, beacon, respawn_pos, camera_offset_x
        nonlocal selected_entity, selected_type, dragging
        selected_entity = None
        selected_type = None
        dragging = False
        if not load_from_checkpoint:
            respawn_pos = (100, 400)
            
        platforms, checkpoints, monkeys, birds, beacon = generate_level()
        
        # Pre-activate the checkpoint if loading from one to prevent spawn sound/dialogue re-trigger
        if load_from_checkpoint:
            for cp in checkpoints:
                # Check if this checkpoint aligns with our respawn position
                if abs(cp.rect.x - respawn_pos[0]) < 10 and abs((cp.rect.y - 60) - respawn_pos[1]) < 10:
                    cp.active = True
                    
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
                        stop_bgm()
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
                        stop_bgm()
                elif state == "VICTORY":
                    if hasattr(ui, 'vic_rect') and ui.vic_rect.collidepoint(mouse_pos):
                        state = "MENU"
                        stop_bgm()
                elif state == "EDITOR":
                    # Selection check in Editor Mode
                    mx, my = event.pos[0] + camera_offset_x, event.pos[1]
                    found = False
                    
                    # 1. Player
                    if player and player.rect.collidepoint((mx, my)):
                        selected_entity = player
                        selected_type = "Player"
                        found = True
                    # 2. Beacon
                    elif beacon and beacon.rect.collidepoint((mx, my)):
                        selected_entity = beacon
                        selected_type = "Beacon"
                        found = True
                    # 3. Checkpoints
                    if not found and checkpoints:
                        for cp in checkpoints:
                            if cp.rect.collidepoint((mx, my)):
                                selected_entity = cp
                                selected_type = "Checkpoint"
                                found = True
                                break
                    # 4. Monkeys
                    if not found and monkeys:
                        for m in monkeys:
                            if m.rect.collidepoint((mx, my)):
                                selected_entity = m
                                selected_type = "Monkey"
                                found = True
                                break
                    # 5. Birds
                    if not found and birds:
                        for b in birds:
                            if b.rect.collidepoint((mx, my)):
                                selected_entity = b
                                selected_type = "Bird"
                                found = True
                                break
                    # 6. Platforms
                    if not found and platforms:
                        for p in platforms:
                            if p.rect.x != -50 and p.rect.collidepoint((mx, my)):
                                selected_entity = p
                                selected_type = "Platform"
                                found = True
                                break
                                
                    if not found:
                        selected_entity = None
                        selected_type = None
                    else:
                        dragging = True
                        drag_offset_x = selected_entity.rect.x - (event.pos[0] + camera_offset_x)
                        drag_offset_y = selected_entity.rect.y - event.pos[1]

            if event.type == pygame.MOUSEBUTTONUP:
                if state == "EDITOR":
                    dragging = False

            if event.type == pygame.KEYDOWN:
                if state == "STORY" and event.key == pygame.K_SPACE:
                    start_game()
                    state = "PLAYING"
                # Quick respawn from checkpoint for testing/gameplay
                if state == "GAME_OVER" and event.key == pygame.K_r:
                    start_game(load_from_checkpoint=True)
                    state = "PLAYING"
                
                # Toggle Editor Mode
                if state == "PLAYING" and event.key == pygame.K_e:
                    import settings
                    if settings.DEV_MODE:
                        state = "EDITOR"
                        selected_entity = None
                        selected_type = None
                        dragging = False
                elif state == "EDITOR":
                    if event.key == pygame.K_e:
                        state = "PLAYING"
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        from assets import save_level_data
                        save_level_data(platforms, checkpoints, monkeys, birds, beacon)
                        save_success_timer = pygame.time.get_ticks()
                    elif event.key == pygame.K_UP:
                        if selected_entity:
                            from assets import GLOBAL_OFFSETS
                            if selected_type == "Player": GLOBAL_OFFSETS['player'] += 1
                            elif selected_type == "Monkey":
                                GLOBAL_OFFSETS['monkey_stand'] += 1
                                GLOBAL_OFFSETS['monkey_walk'] += 1
                                GLOBAL_OFFSETS['monkey_attack'] += 1
                            elif selected_type == "Bird": GLOBAL_OFFSETS['bird'] += 1
                            elif selected_type == "Checkpoint": GLOBAL_OFFSETS['checkpoint'] += 1
                            elif selected_type == "Beacon": GLOBAL_OFFSETS['beacon'] += 1
                    elif event.key == pygame.K_DOWN:
                        if selected_entity:
                            from assets import GLOBAL_OFFSETS
                            if selected_type == "Player": GLOBAL_OFFSETS['player'] -= 1
                            elif selected_type == "Monkey":
                                GLOBAL_OFFSETS['monkey_stand'] -= 1
                                GLOBAL_OFFSETS['monkey_walk'] -= 1
                                GLOBAL_OFFSETS['monkey_attack'] -= 1
                            elif selected_type == "Bird": GLOBAL_OFFSETS['bird'] -= 1
                            elif selected_type == "Checkpoint": GLOBAL_OFFSETS['checkpoint'] -= 1
                            elif selected_type == "Beacon": GLOBAL_OFFSETS['beacon'] -= 1

        # State updates & rendering
        if state == "MENU":
            ui.draw_menu(screen)
            
        elif state == "STORY":
            ui.draw_story(screen)
            
        elif state == "PLAYING":
            # Start BGM if not already playing
            play_bgm('bgm.ogg', 0.4)
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
                    SOUNDS['checkpoint'].play()
                    
            # Beacon collision
            if player.rect.colliderect(beacon.rect):
                state = "VICTORY"
                SOUNDS['beacon'].play()
                stop_bgm()

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

        elif state == "EDITOR":
            # Camera scroll inside Editor Mode
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                camera_offset_x -= 12
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                camera_offset_x += 12
            if camera_offset_x < 0:
                camera_offset_x = 0
                
            # Dragging update
            if dragging and selected_entity:
                selected_entity.rect.x = mouse_pos[0] + camera_offset_x + drag_offset_x
                selected_entity.rect.y = mouse_pos[1] + drag_offset_y
                # Anchor updates
                if selected_type == "Monkey":
                    selected_entity.patrol_anchor = selected_entity.rect.x
                elif selected_type == "Bird":
                    selected_entity.patrol_anchor_x = selected_entity.rect.x
                    selected_entity.patrol_anchor_y = selected_entity.rect.y
            
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
            
            # Highlight selected entity with yellow outline box
            if selected_entity:
                outline_rect = selected_entity.rect.copy()
                outline_rect.x -= camera_offset_x
                pygame.draw.rect(screen, (255, 255, 0), outline_rect, 2)
                
            # Draw editor HUD overlay
            from assets import GLOBAL_OFFSETS
            ui.draw_editor_hud(screen, selected_entity, selected_type, GLOBAL_OFFSETS, save_success_timer)

        elif state == "GAME_OVER":
            ui.draw_game_over(screen)
            
        elif state == "VICTORY":
            ui.draw_victory(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main()
