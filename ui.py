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

    def draw_editor_hud(self, surface, selected_entity, selection_type, offsets_dict, save_success_timer=0):
        # Draw dark border/panel at top
        panel_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 140)
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height))
        panel_surf.fill((10, 15, 25))
        panel_surf.set_alpha(220)
        surface.blit(panel_surf, panel_rect)
        pygame.draw.line(surface, (0, 180, 216), (0, 140), (WINDOW_WIDTH, 140), 2)
        
        # Title
        title_surf = self.subtitle_font.render("MODO EDITOR DE NÍVEL & ALTURAS", True, (0, 180, 216))
        surface.blit(title_surf, (20, 15))
        
        # Instructions
        inst = [
            "• CLIQUE E ARRASTE elementos (Plataformas, Checkpoints, Beacon, Inimigos, Jogador)",
            "• SETAS CIMA / BAIXO: Ajusta a altura (Y-Offset) visual do elemento selecionado",
            "• ENTER: Salvar no arquivo level_data.json  |  TECLA E: Voltar ao Jogo"
        ]
        
        y_offset = 55
        for line in inst:
            line_surf = self.text_font.render(line, True, (200, 200, 220))
            surface.blit(line_surf, (20, y_offset))
            y_offset += 25
            
        # Selection info panel (on the right)
        info_rect = pygame.Rect(WINDOW_WIDTH - 450, 10, 430, 120)
        pygame.draw.rect(surface, (20, 28, 42), info_rect)
        pygame.draw.rect(surface, (0, 180, 216), info_rect, 1)
        
        if selected_entity:
            name_surf = self.subtitle_font.render(f"Selecionado: {selection_type}", True, (255, 255, 100))
            surface.blit(name_surf, (WINDOW_WIDTH - 430, 20))
            
            x_y_surf = self.text_font.render(f"Posição Spawn: X={selected_entity.rect.x}, Y={selected_entity.rect.y}", True, COLOR_TEXT)
            surface.blit(x_y_surf, (WINDOW_WIDTH - 430, 55))
            
            # Show Y offset if applicable
            offset_key = None
            if selection_type == "Player": offset_key = "player"
            elif selection_type == "Monkey": offset_key = "monkey_stand"
            elif selection_type == "Bird": offset_key = "bird"
            elif selection_type == "Checkpoint": offset_key = "checkpoint"
            elif selection_type == "Beacon": offset_key = "beacon"
            
            if offset_key and offset_key in offsets_dict:
                offset_val = offsets_dict[offset_key]
                offset_surf = self.text_font.render(f"Ajuste Sprite Y-Offset: {offset_val}px (Setas Cima/Baixo)", True, (100, 255, 100))
                surface.blit(offset_surf, (WINDOW_WIDTH - 430, 85))
            else:
                desc_surf = self.text_font.render("Plataforma física (sem offset de imagem)", True, (180, 180, 180))
                surface.blit(desc_surf, (WINDOW_WIDTH - 430, 85))
        else:
            empty_surf = self.subtitle_font.render("Nenhum item selecionado", True, (150, 150, 150))
            surface.blit(empty_surf, (WINDOW_WIDTH - 410, 35))
            desc_surf = self.text_font.render("Clique em um item para arrastar ou calibrar", True, (150, 150, 150))
            surface.blit(desc_surf, (WINDOW_WIDTH - 410, 70))
            
        # Success message overlay
        current_time = pygame.time.get_ticks()
        if save_success_timer > 0 and current_time - save_success_timer < 2500:
            success_bg = pygame.Surface((WINDOW_WIDTH, 50))
            success_bg.fill((10, 80, 40))
            success_bg.set_alpha(200)
            surface.blit(success_bg, (0, 142))
            
            success_surf = self.subtitle_font.render("NÍVEL E OFFSETS SALVOS COM SUCESSO EM Assets/level_data.json! 💾", True, (100, 255, 100))
            success_rect = success_surf.get_rect(center=(WINDOW_WIDTH//2, 167))
            surface.blit(success_surf, success_rect)
