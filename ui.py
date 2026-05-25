import pygame
from settings import *

class UI:
    def __init__(self):
        pygame.font.init()
        # Default fallback font
        self.title_font = pygame.font.SysFont("arial", 80, bold=True)
        self.subtitle_font = pygame.font.SysFont("arial", 30, italic=True)
        self.button_font = pygame.font.SysFont("arial", 40)
        self.text_font = pygame.font.SysFont("arial", 24)
        self.lore_font = pygame.font.SysFont("arial", 36, italic=True)

        self.lore_text = ""
        self.lore_timer = 0
        self.lore_duration = 4000 # ms

    def draw_menu(self, surface):
        surface.fill(COLOR_BG)
        
        # Title
        title_surf = self.title_font.render("MAYDAY", True, COLOR_TEXT)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH//2, 200))
        surface.blit(title_surf, title_rect)
        
        # Subtitle
        sub_surf = self.subtitle_font.render('"A Terra não te esqueceu. Ela só evoluiu para te matar."', True, (200, 200, 200))
        sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH//2, 280))
        surface.blit(sub_surf, sub_rect)
        
        # Buttons
        import settings
        dev_status = "ATIVO" if settings.DEV_MODE else "INATIVO"
        buttons = [
            ("INICIAR MISSÃO", 400),
            (f"MODO DEV: {dev_status}", 500),
            ("SAIR", 600)
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        clicked_button = None
        
        self.button_rects = {}
        for text, y in buttons:
            btn_surf = self.button_font.render(f"[ {text} ]", True, COLOR_TEXT)
            btn_rect = btn_surf.get_rect(center=(WINDOW_WIDTH//2, y))
            
            # Hover effect
            if btn_rect.collidepoint(mouse_pos):
                btn_surf = self.button_font.render(f"> {text} <", True, (255, 255, 100))
                
            surface.blit(btn_surf, btn_rect)
            self.button_rects[text] = btn_rect
            
    def get_menu_click(self, mouse_pos):
        if not hasattr(self, 'button_rects'): return None
        for text, rect in self.button_rects.items():
            if rect.collidepoint(mouse_pos):
                return text
        return None

    def draw_story(self, surface):
        surface.fill((10, 10, 15))
        
        story = [
            "O ano é 3247. Há mais de mil anos, a humanidade abandonou a Terra.",
            "A fauna passou por mutações aceleradas e imprevisíveis.",
            "A nave MAYDAY-7 foi atingida por detritos e partiu ao meio.",
            "Apenas você, Sgt. Kael Voss, sobreviveu ao impacto.",
            "",
            "15 quilômetros de selva evoluída para matar te separam da sobrevivência.",
            "Chegue ao sinalizador na seção dianteira da nave.",
            "",
            "(Clique ou pressione Espaço para continuar)"
        ]
        
        y = 150
        for line in story:
            text_surf = self.text_font.render(line, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH//2, y))
            surface.blit(text_surf, text_rect)
            y += 50

    def draw_hud(self, surface, player):
        # HP Bar
        pygame.draw.rect(surface, COLOR_HP_BG, (20, 20, 300, 30))
        hp_width = int(300 * (player.hp / player.max_hp if hasattr(player, 'max_hp') else player.hp / PLAYER_MAX_HP))
        if hp_width > 0:
            pygame.draw.rect(surface, COLOR_HP_FG, (20, 20, hp_width, 30))
            
        hp_text = self.text_font.render(f"HP: {player.hp}/{PLAYER_MAX_HP}", True, COLOR_TEXT)
        surface.blit(hp_text, (25, 22))

        import settings
        if settings.DEV_MODE:
            dev_surf = self.text_font.render("MODO DEV ATIVO [ SEGURE W / ESPAÇO PARA VOAR | INVENCÍVEL ]", True, (255, 255, 100))
            surface.blit(dev_surf, (20, 60))

        # Checkpoint Lore Text
        current_time = pygame.time.get_ticks()
        if self.lore_text and current_time - self.lore_timer < self.lore_duration:
            # Fade out effect
            alpha = 255
            time_left = self.lore_duration - (current_time - self.lore_timer)
            if time_left < 1000:
                alpha = int(255 * (time_left / 1000))
                
            lore_surf = self.lore_font.render(self.lore_text, True, (255, 255, 200))
            lore_surf.set_alpha(alpha)
            lore_rect = lore_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 100))
            
            # Draw semi-transparent background for readability
            bg_rect = lore_rect.copy()
            bg_rect.inflate_ip(40, 20)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surf.fill((0, 0, 0))
            bg_surf.set_alpha(int(alpha * 0.7))
            surface.blit(bg_surf, bg_rect)
            
            surface.blit(lore_surf, lore_rect)

    def show_lore(self, text):
        self.lore_text = text
        self.lore_timer = pygame.time.get_ticks()

    def draw_game_over(self, surface):
        surface.fill((50, 10, 10))
        
        title = self.title_font.render("GAME OVER", True, (255, 50, 50))
        surface.blit(title, title.get_rect(center=(WINDOW_WIDTH//2, 200)))
        
        msg = self.text_font.render('"A Terra recuperou mais um. O sinalizador nunca foi ativado. Ninguém veio."', True, COLOR_TEXT)
        surface.blit(msg, msg.get_rect(center=(WINDOW_WIDTH//2, 300)))
        
        mouse_pos = pygame.mouse.get_pos()
        
        btn_respawn = self.button_font.render("[ TENTAR NOVAMENTE ]", True, COLOR_TEXT)
        self.go_respawn_rect = btn_respawn.get_rect(center=(WINDOW_WIDTH//2, 450))
        if self.go_respawn_rect.collidepoint(mouse_pos):
            btn_respawn = self.button_font.render("> TENTAR NOVAMENTE <", True, (255, 255, 100))
        surface.blit(btn_respawn, self.go_respawn_rect)
        
        btn_menu = self.button_font.render("[ VOLTAR AO MENU ]", True, COLOR_TEXT)
        self.go_menu_rect = btn_menu.get_rect(center=(WINDOW_WIDTH//2, 550))
        if self.go_menu_rect.collidepoint(mouse_pos):
            btn_menu = self.button_font.render("> VOLTAR AO MENU <", True, (255, 255, 100))
        surface.blit(btn_menu, self.go_menu_rect)

    def get_game_over_click(self, mouse_pos):
        if hasattr(self, 'go_respawn_rect') and self.go_respawn_rect.collidepoint(mouse_pos):
            return "TENTAR NOVAMENTE"
        if hasattr(self, 'go_menu_rect') and self.go_menu_rect.collidepoint(mouse_pos):
            return "VOLTAR AO MENU"
        return None

    def draw_victory(self, surface):
        surface.fill((10, 50, 10))
        
        title = self.title_font.render("MISSÃO CUMPRIDA", True, (50, 255, 50))
        surface.blit(title, title.get_rect(center=(WINDOW_WIDTH//2, 250)))
        
        msg1 = self.text_font.render('"O sinal foi enviado. Nas estrelas, alguém ouviu."', True, COLOR_TEXT)
        surface.blit(msg1, msg1.get_rect(center=(WINDOW_WIDTH//2, 350)))
        
        msg2 = self.text_font.render('"Pela primeira vez em mil anos, um humano sobreviveu à Terra — e ela ainda não sabe o que fazer com isso."', True, COLOR_TEXT)
        surface.blit(msg2, msg2.get_rect(center=(WINDOW_WIDTH//2, 400)))
        
        btn = self.button_font.render("[ VOLTAR AO MENU ]", True, COLOR_TEXT)
        self.vic_rect = btn.get_rect(center=(WINDOW_WIDTH//2, 550))
        surface.blit(btn, self.vic_rect)
