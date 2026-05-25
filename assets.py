import pygame
import sys
import os
import settings

IMAGES = {}
SOUNDS = {}
GLOBAL_OFFSETS = {
    'player': 0,
    'monkey_stand': -14,
    'monkey_walk': -10,
    'monkey_attack': -14,
    'bird': -5,
    'checkpoint': 0,
    'beacon': 0
}

class SafeSound:
    """ A wrapper around pygame.mixer.Sound to handle missing or failed sound loads gracefully. """
    def __init__(self, filename):
        self.sound = None
        self.filename = filename
        path = resource_path(os.path.join('Assets/Sounds', filename))
        if pygame.mixer.get_init():
            if os.path.exists(path):
                try:
                    self.sound = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"Warning: Failed to load sound {filename}: {e}")
            else:
                # Silently ignore missing files
                pass

    def play(self, loops=0, maxtime=0, fade_ms=0):
        if self.sound:
            try:
                return self.sound.play(loops, maxtime, fade_ms)
            except Exception:
                pass
        return None

    def stop(self):
        if self.sound:
            try:
                self.sound.stop()
            except Exception:
                pass

    def set_volume(self, volume):
        if self.sound:
            try:
                self.sound.set_volume(volume)
            except Exception:
                pass

def play_bgm(filename, volume=0.4):
    """ Loads and plays a background music track seamlessly, checking if it is already playing. """
    if pygame.mixer.get_init():
        path = resource_path(os.path.join('Assets/Sounds', filename))
        if os.path.exists(path):
            try:
                if pygame.mixer.music.get_busy():
                    return
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1) # Loop indefinitely
            except Exception as e:
                print(f"Warning: Failed to play BGM {filename}: {e}")
        else:
            # Silent fallback
            pass

def stop_bgm():
    """ Safely stops the background music if mixer is initialized. """
    if pygame.mixer.get_init():
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # Prioritize local file if it exists next to the executable/script
    local_path = os.path.join(os.path.abspath("."), relative_path)
    if os.path.exists(local_path):
        return local_path

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def download_font(filename, url):
    """ Downloads a font from a URL into Assets/Fonts if it doesn't exist. """
    font_dir = 'Assets/Fonts'
    font_path = os.path.join(font_dir, filename)
    if not os.path.exists(font_path):
        try:
            os.makedirs(font_dir, exist_ok=True)
            import urllib.request
            print(f"Downloading premium font {filename} from Google Fonts...")
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                with open(font_path, 'wb') as out_file:
                    out_file.write(response.read())
            print(f"Font {filename} successfully downloaded!")
        except Exception as e:
            print(f"Warning: Failed to download font {filename}: {e}")
    return font_path

def set_master_volume(volume):
    """ Sets the volume for background music and all active sound effects. """
    import settings
    settings.MASTER_VOLUME = volume
    if pygame.mixer.get_init():
        try:
            pygame.mixer.music.set_volume(volume)
        except Exception:
            pass
        for s in SOUNDS.values():
            s.set_volume(volume)

def load_assets():
    # Download premium fonts if missing
    download_font('Orbitron-Bold.ttf', 'https://github.com/google/fonts/raw/main/ofl/orbitron/static/Orbitron-Bold.ttf')
    download_font('Rajdhani-Medium.ttf', 'https://github.com/google/fonts/raw/main/ofl/rajdhani/Rajdhani-Medium.ttf')

    # Load offsets from JSON if it exists
    import json
    data_path = resource_path('Assets/level_data.json')
    if os.path.exists(data_path):
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                if 'offsets' in saved_data:
                    GLOBAL_OFFSETS.update(saved_data['offsets'])
        except Exception as e:
            print(f"Warning: Failed to load level_data offsets: {e}")

    # Initialize mixer if not already initialized with optimized low-latency settings
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init(44100, -16, 2, 512)
        except Exception as e:
            print(f"Warning: Could not initialize pygame mixer: {e}")

    # Load Sound Effects
    SOUNDS['jump'] = SafeSound('jump.wav')
    SOUNDS['light_attack'] = SafeSound('light_attack.wav')
    SOUNDS['heavy_attack'] = SafeSound('heavy_attack.wav')
    SOUNDS['player_damage'] = SafeSound('player_damage.wav')
    SOUNDS['enemy_damage'] = SafeSound('enemy_damage.wav')
    SOUNDS['monkey_attack'] = SafeSound('monkey_attack.wav')
    SOUNDS['bird_attack'] = SafeSound('bird_attack.wav')
    SOUNDS['checkpoint'] = SafeSound('checkpoint.wav')
    SOUNDS['beacon'] = SafeSound('beacon.wav')
    # Apply master volume
    set_master_volume(settings.MASTER_VOLUME)
    
    # Background
    bg_path = resource_path('Assets/Background.png')
    if os.path.exists(bg_path):
        bg_img = pygame.transform.scale(pygame.image.load(bg_path).convert(), (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        # Create a vertical gradient mask to dim the background and highlight the player/enemies
        gradient = pygame.Surface((1, settings.WINDOW_HEIGHT), pygame.SRCALPHA)
        for y in range(settings.WINDOW_HEIGHT):
            # Alpha goes from 210 at the top (very dark) to 120 at the bottom (moderately dark)
            alpha = int(215 - (y / settings.WINDOW_HEIGHT) * 95)
            gradient.set_at((0, y), (10, 10, 18, alpha)) # Dark blue-black night filter
        gradient_scaled = pygame.transform.scale(gradient, (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        bg_img.blit(gradient_scaled, (0, 0))
        IMAGES['bg'] = bg_img
    else:
        # Fallback
        surf = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
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

def save_level_data(platforms, checkpoints, monkeys, birds, beacon):
    """ Saves platforms, checkpoints, monkeys, birds, beacon coordinates and global offsets to level_data.json. """
    import json
    # Gather platforms
    platform_list = []
    for p in platforms:
        platform_list.append({
            'x': p.rect.x,
            'y': p.rect.y,
            'width': p.rect.width,
            'height': p.rect.height
        })
        
    # Gather checkpoints
    checkpoint_list = []
    for cp in checkpoints:
        checkpoint_list.append({
            'x': cp.rect.x,
            'y': cp.rect.y,
            'text_id': cp.text_id,
            'text_content': cp.text_content
        })
        
    # Gather monkeys
    monkey_list = []
    for m in monkeys:
        monkey_list.append({
            'x': m.patrol_anchor,
            'y': m.rect.y
        })
        
    # Gather birds
    bird_list = []
    for b in birds:
        bird_list.append({
            'x': b.patrol_anchor_x,
            'y': b.patrol_anchor_y
        })
        
    # Gather beacon
    beacon_data = {
        'x': beacon.rect.x,
        'y': beacon.rect.y
    }
    
    # Bundle everything
    level_data = {
        'offsets': GLOBAL_OFFSETS,
        'platforms': platform_list,
        'checkpoints': checkpoint_list,
        'monkeys': monkey_list,
        'birds': bird_list,
        'beacon': beacon_data
    }
    
    # Save to file
    try:
        os.makedirs('Assets', exist_ok=True)
        # Save to local Assets folder
        with open('Assets/level_data.json', 'w', encoding='utf-8') as f:
            json.dump(level_data, f, indent=4, ensure_ascii=False)
        print("Level and Offsets data successfully saved to Assets/level_data.json!")
        return True
    except Exception as e:
        print(f"Error saving level data: {e}")
        return False
