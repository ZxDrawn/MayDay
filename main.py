# main.py
# Main Game Loop and State Machine with Dynamic UI & Settings for Mayday

import pygame
import sys
import os
import settings
from settings import *
from entities import Player
from level import generate_level
from ui import UI
from assets import load_assets, IMAGES, SOUNDS, play_bgm, stop_bgm, resource_path, set_master_volume

def load_settings():
    """ Loads settings from settings_data.json if it exists, initializing global variables """
    settings_path = resource_path('Assets/settings_data.json')
    if os.path.exists(settings_path):
        try:
            import json
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'resolution' in data:
                res = data['resolution']
                settings.WINDOW_WIDTH = res.get('width', 1280)
                settings.WINDOW_HEIGHT = res.get('height', 720)
            if 'fullscreen' in data:
                settings.IS_FULLSCREEN = data['fullscreen']
            if 'volume' in data:
                settings.MASTER_VOLUME = data['volume']
            if 'show_fps' in data:
                settings.SHOW_FPS = data['show_fps']
            if 'dev_mode' in data:
                settings.DEV_MODE = data['dev_mode']
        except Exception as e:
            print(f"Warning: Failed to load settings: {e}")

def save_settings():
    """ Saves current settings variables to Assets/settings_data.json """
    data = {
        'resolution': {
            'width': settings.WINDOW_WIDTH,
            'height': settings.WINDOW_HEIGHT
        },
        'fullscreen': settings.IS_FULLSCREEN,
        'volume': settings.MASTER_VOLUME,
        'show_fps': settings.SHOW_FPS,
        'dev_mode': settings.DEV_MODE
    }
    try:
        import json
        os.makedirs('Assets', exist_ok=True)
        with open('Assets/settings_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Settings saved successfully!")
    except Exception as e:
        print(f"Error saving settings: {e}")

def main():
    pygame.init()
    
    # Load settings prior to display initialization
    load_settings()
    
    # Re-apply master volume to low-latency mixer setup
    set_master_volume(settings.MASTER_VOLUME)
    
    flags = pygame.FULLSCREEN if settings.IS_FULLSCREEN else 0
    screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), flags)
    pygame.display.set_caption("MAYDAY")
    
    # Load assets (scaled to the current resolution settings)
    load_assets()
    
    clock = pygame.time.Clock()

    state = "MENU" # MENU, STORY, PLAYING, GAME_OVER, VICTORY, SETTINGS, PAUSED
    settings_back_state = "MENU"
    story_stage = 0
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
    
    # Slider dragging state for Settings
    volume_dragging = False

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
        camera_offset_x = player.rect.centerx - settings.WINDOW_WIDTH // 2

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
                        story_stage = 0
                    elif clicked == "CONFIGURAÇÕES":
                        state = "SETTINGS"
                        settings_back_state = "MENU"
                        volume_dragging = False
                    elif clicked == "SAIR":
                        stop_bgm()
                        pygame.quit()
                        sys.exit()
                elif state == "PAUSED":
                    clicked = ui.get_pause_click(mouse_pos)
                    if clicked == "CONTINUAR":
                        state = "PLAYING"
                        play_bgm('bgm.ogg', settings.MASTER_VOLUME)
                    elif clicked == "CONFIGURAÇÕES":
                        state = "SETTINGS"
                        settings_back_state = "PAUSED"
                        volume_dragging = False
                    elif clicked == "VOLTAR AO MENU":
                        state = "MENU"
                        stop_bgm()
                elif state == "STORY":
                    if story_stage < 3:
                        story_stage += 1
                    else:
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
                elif state == "SETTINGS":
                    # Handle settings options click
                    for label, rect in ui.setting_rects.items():
                        if rect.collidepoint(mouse_pos):
                            if label == "RESOLUÇÃO":
                                # Cycle resolutions
                                if settings.WINDOW_WIDTH == 1280:
                                    settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT = 1600, 900
                                elif settings.WINDOW_WIDTH == 1600:
                                    settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT = 1920, 1080
                                else:
                                    settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT = 1280, 720
                                # Apply resolution change
                                flags = pygame.FULLSCREEN if settings.IS_FULLSCREEN else 0
                                screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), flags)
                                load_assets()
                                # Reload UI sizes
                                ui = UI()
                            elif label == "TELA":
                                settings.IS_FULLSCREEN = not settings.IS_FULLSCREEN
                                flags = pygame.FULLSCREEN if settings.IS_FULLSCREEN else 0
                                screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), flags)
                                load_assets()
                                ui = UI()
                            elif label == "EXIBIR FPS":
                                settings.SHOW_FPS = not settings.SHOW_FPS
                            elif label == "MODO DEV":
                                settings.DEV_MODE = not settings.DEV_MODE
                            elif label == "VOLTAR":
                                save_settings()
                                state = settings_back_state
                    
                    # Handle volume slider press
                    if ui.slider_rect.collidepoint(mouse_pos):
                        volume_dragging = True
                        mx = mouse_pos[0]
                        vol = (mx - ui.slider_rect.x) / ui.slider_rect.width
                        vol = max(0.0, min(1.0, vol))
                        set_master_volume(vol)
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
                if state == "SETTINGS":
                    volume_dragging = False
                elif state == "EDITOR":
                    dragging = False

            if event.type == pygame.KEYDOWN:
                if state == "STORY" and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    if story_stage < 3:
                        story_stage += 1
                    else:
                        start_game()
                        state = "PLAYING"
                # Quick respawn from checkpoint for testing/gameplay
                if state == "GAME_OVER" and event.key == pygame.K_r:
                    start_game(load_from_checkpoint=True)
                    state = "PLAYING"
                
                # Toggle Pause Menu with ESC
                if state == "PLAYING" and event.key == pygame.K_ESCAPE:
                    state = "PAUSED"
                    play_bgm('bgm.ogg', settings.MASTER_VOLUME * 0.3)
                elif state == "PAUSED" and event.key == pygame.K_ESCAPE:
                    state = "PLAYING"
                    play_bgm('bgm.ogg', settings.MASTER_VOLUME)
                
                # Toggle Editor Mode
                if state == "PLAYING" and event.key == pygame.K_e:
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

        # Continuous volume slider dragging update
        if state == "SETTINGS" and volume_dragging:
            mx = mouse_pos[0]
            vol = (mx - ui.slider_rect.x) / ui.slider_rect.width
            vol = max(0.0, min(1.0, vol))
            set_master_volume(vol)

        # State updates & rendering
        if state == "MENU":
            ui.draw_menu(screen)
            
        elif state == "SETTINGS":
            ui.draw_settings(screen)
            
        elif state == "STORY":
            ui.draw_story(screen, story_stage)
            
        elif state == "PLAYING" or state == "PAUSED":
            if state == "PLAYING":
                # Start BGM if not already playing with configured MASTER_VOLUME
                play_bgm('bgm.ogg', settings.MASTER_VOLUME)
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
                target_camera_x = player.rect.centerx - settings.WINDOW_WIDTH // 2
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
            
            # HUD
            ui.draw_hud(screen, player)
            
            # Render styled FPS counter overlay if enabled
            if settings.SHOW_FPS:
                fps_text = ui.text_font.render(f"FPS: {int(clock.get_fps())}", True, (46, 196, 182))
                # draw on top right corner
                screen.blit(fps_text, (settings.WINDOW_WIDTH - fps_text.get_width() - 30, 70))

            # Pause Overlay
            if state == "PAUSED":
                ui.draw_pause_menu(screen)

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
