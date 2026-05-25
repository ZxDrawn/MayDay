# ui.py
# Modernized Premium Cyberpunk UI for Mayday

import pygame
import math
import settings
from settings import *

class UI:
    def __init__(self):
        pygame.font.init()
        from assets import resource_path
        import os
        
        # Load premium sci-fi/cyberpunk fonts with system fallbacks
        font_orbitron = resource_path('Assets/Fonts/Orbitron-Bold.ttf')
        font_rajdhani = resource_path('Assets/Fonts/Rajdhani-Medium.ttf')
        
        try:
            if os.path.exists(font_orbitron):
                self.title_font = pygame.font.Font(font_orbitron, 84)
                self.sec_title_font = pygame.font.Font(font_orbitron, 48)
            else:
                self.title_font = pygame.font.SysFont("arial", 80, bold=True)
                self.sec_title_font = pygame.font.SysFont("arial", 45, bold=True)
        except Exception:
            self.title_font = pygame.font.SysFont("arial", 80, bold=True)
            self.sec_title_font = pygame.font.SysFont("arial", 45, bold=True)
            
        try:
            if os.path.exists(font_rajdhani):
                self.subtitle_font = pygame.font.Font(font_rajdhani, 30)
                self.button_font = pygame.font.Font(font_rajdhani, 34)
                self.text_font = pygame.font.Font(font_rajdhani, 22)
                self.lore_font = pygame.font.Font(font_rajdhani, 28)
            else:
                self.subtitle_font = pygame.font.SysFont("arial", 28, italic=True)
                self.button_font = pygame.font.SysFont("arial", 36)
                self.text_font = pygame.font.SysFont("arial", 22)
                self.lore_font = pygame.font.SysFont("arial", 32, italic=True)
        except Exception:
            self.subtitle_font = pygame.font.SysFont("arial", 28, italic=True)
            self.button_font = pygame.font.SysFont("arial", 36)
            self.text_font = pygame.font.SysFont("arial", 22)
            self.lore_font = pygame.font.SysFont("arial", 32, italic=True)

        self.lore_text = ""
        self.lore_timer = 0
        self.lore_duration = 4000 # ms
        self.slider_rect = pygame.Rect(0, 0, 300, 16) # initialized dynamically

    def draw_grid_effect(self, surface):
        """ Draws a subtle glowing tech grid on the background for a modern sci-fi atmosphere """
        w, h = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
        grid_color = (0, 180, 216, 20) # extremely faint ciano
        grid_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        
        spacing = 64
        for x in range(0, w, spacing):
            pygame.draw.line(grid_surface, grid_color, (x, 0), (x, h), 1)
        for y in range(0, h, spacing):
            pygame.draw.line(grid_surface, grid_color, (0, y), (w, y), 1)
            
        surface.blit(grid_surface, (0, 0))

    def draw_button(self, surface, text, x, y, width, height, mouse_pos):
        """ Draws a modern capsule button with neon glow, hover scale and sound-feedback ready borders """
        btn_rect = pygame.Rect(0, 0, width, height)
        btn_rect.center = (x, y)
        
        is_hovered = btn_rect.collidepoint(mouse_pos)
        
        # Micro-scale animation when hovered
        if is_hovered:
            btn_rect.inflate_ip(12, 6)
            bg_color = (15, 42, 65, 230)
            border_color = (72, 202, 228) # Electric ciano
            text_color = (255, 255, 255)
            # Faint neon glow aura
            glow_surf = pygame.Surface((btn_rect.width + 10, btn_rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (0, 180, 216, 40), (0, 0, btn_rect.width + 10, btn_rect.height + 10), border_radius=10)
            surface.blit(glow_surf, (btn_rect.x - 5, btn_rect.y - 5))
            
            disp_text = f">  {text}  <"
        else:
            bg_color = (20, 26, 38, 200)
            border_color = (0, 180, 216) # Neon turquesa
            text_color = (200, 220, 240)
            disp_text = text
            
        # Draw background capsule
        btn_surf = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, bg_color, (0, 0, btn_rect.width, btn_rect.height), border_radius=6)
        pygame.draw.rect(btn_surf, border_color, (0, 0, btn_rect.width, btn_rect.height), 2, border_radius=6)
        
        surface.blit(btn_surf, btn_rect)
        
        # Render text
        text_surf = self.button_font.render(disp_text, True, text_color)
        text_rect = text_surf.get_rect(center=btn_rect.center)
        surface.blit(text_surf, text_rect)
        
        return btn_rect

    def draw_menu(self, surface):
        w, h = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
        surface.fill(COLOR_BG)
        self.draw_grid_effect(surface)
        
        # Hologram panel aura
        panel_surf = pygame.Surface((700, 520), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (10, 15, 25, 160), (0, 0, 700, 520), border_radius=12)
        pygame.draw.rect(panel_surf, (0, 180, 216, 50), (0, 0, 700, 520), 2, border_radius=12)
        surface.blit(panel_surf, panel_surf.get_rect(center=(w//2, h//2 + 40)))
        
        # Title with cyan shadow glow
        glow_title = self.title_font.render("MAYDAY", True, (0, 119, 182))
        surface.blit(glow_title, glow_title.get_rect(center=(w//2 + 3, h//2 - 198)))
        
        title_surf = self.title_font.render("MAYDAY", True, COLOR_TEXT)
        title_rect = title_surf.get_rect(center=(w//2, h//2 - 200))
        surface.blit(title_surf, title_rect)
        
        # Subtitle
        sub_surf = self.subtitle_font.render('"A Terra não te esqueceu. Ela só evoluiu para te matar."', True, (0, 180, 216))
        sub_rect = sub_surf.get_rect(center=(w//2, h//2 - 120))
        surface.blit(sub_surf, sub_rect)
        
        # Buttons
        buttons = [
            ("INICIAR MISSÃO", h//2 - 20),
            ("CONFIGURAÇÕES", h//2 + 60),
            ("SAIR", h//2 + 140)
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        self.button_rects = {}
        
        for text, y in buttons:
            rect = self.draw_button(surface, text, w//2, y, 360, 56, mouse_pos)
            self.button_rects[text] = rect
            
    def get_menu_click(self, mouse_pos):
        if not hasattr(self, 'button_rects'): return None
        for text, rect in self.button_rects.items():
            if rect.collidepoint(mouse_pos):
                return text
        return None

    def draw_settings(self, surface):
        w, h = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
        surface.fill(COLOR_BG)
        self.draw_grid_effect(surface)
        
        # Glow panel
        panel_surf = pygame.Surface((800, 540), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (10, 15, 25, 190), (0, 0, 800, 540), border_radius=12)
        pygame.draw.rect(panel_surf, (0, 180, 216, 60), (0, 0, 800, 540), 2, border_radius=12)
        surface.blit(panel_surf, panel_surf.get_rect(center=(w//2, h//2)))
        
        # Title
        title_surf = self.sec_title_font.render("CONFIGURAÇÕES", True, COLOR_TEXT)
        surface.blit(title_surf, title_surf.get_rect(center=(w//2, h//2 - 210)))
        
        mouse_pos = pygame.mouse.get_pos()
        self.setting_rects = {}
        
        # Settings List
        res_str = f"{settings.WINDOW_WIDTH}x{settings.WINDOW_HEIGHT}"
        screen_str = "TELA CHEIA" if settings.IS_FULLSCREEN else "JANELA"
        dev_str = "ATIVO" if settings.DEV_MODE else "INATIVO"
        fps_str = "SIM" if settings.SHOW_FPS else "NÃO"
        
        rows = [
            ("RESOLUÇÃO", res_str, h//2 - 120),
            ("TELA", screen_str, h//2 - 60),
            ("EXIBIR FPS", fps_str, h//2),
            ("MODO DEV", dev_str, h//2 + 60)
        ]
        
        for label, val, y in rows:
            # Draw label
            lbl_surf = self.subtitle_font.render(label, True, (0, 180, 216))
            surface.blit(lbl_surf, (w//2 - 340, y - lbl_surf.get_height()//2))
            
            # Draw interactive value capsule
            rect = self.draw_button(surface, val, w//2 + 160, y, 260, 44, mouse_pos)
            self.setting_rects[label] = rect
            
        # Volume Slider Row
        vol_y = h//2 + 120
        vol_lbl = self.subtitle_font.render("VOLUME GERAL", True, (0, 180, 216))
        surface.blit(vol_lbl, (w//2 - 340, vol_y - vol_lbl.get_height()//2))
        
        # Draw Slider Bar
        self.slider_rect = pygame.Rect(w//2 + 30, vol_y - 8, 260, 16)
        pygame.draw.rect(surface, (20, 32, 48), self.slider_rect, border_radius=8)
        pygame.draw.rect(surface, (0, 180, 216), self.slider_rect, 1, border_radius=8)
        
        # Fill active part
        fill_w = int(self.slider_rect.width * settings.MASTER_VOLUME)
        if fill_w > 0:
            fill_rect = pygame.Rect(self.slider_rect.x, self.slider_rect.y, fill_w, self.slider_rect.height)
            pygame.draw.rect(surface, (0, 180, 216), fill_rect, border_radius=8)
            
        # Draw volume handle/slider knob
        knob_x = self.slider_rect.x + fill_w
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, vol_y), 11)
        pygame.draw.circle(surface, (0, 180, 216), (knob_x, vol_y), 7)
        
        vol_text = self.text_font.render(f"{int(settings.MASTER_VOLUME * 100)}%", True, COLOR_TEXT)
        surface.blit(vol_text, (self.slider_rect.right + 20, vol_y - vol_text.get_height()//2))
        
        # Navigation Buttons at bottom
        self.setting_rects["VOLTAR"] = self.draw_button(surface, "SALVAR E VOLTAR", w//2, h//2 + 200, 320, 50, mouse_pos)

    def draw_story(self, surface):
        w, h = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
        surface.fill((10, 10, 15))
        self.draw_grid_effect(surface)
        
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
        
        # Styled Story panel
        panel_surf = pygame.Surface((900, 520), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (15, 20, 32, 210), (0, 0, 900, 520), border_radius=12)
        pygame.draw.rect(panel_surf, (0, 180, 216, 45), (0, 0, 900, 520), 1, border_radius=12)
        surface.blit(panel_surf, panel_surf.get_rect(center=(w//2, h//2)))
        
        y = h//2 - 200
        for line in story:
            color = (255, 255, 100) if "Clique" in line else COLOR_TEXT
            text_surf = self.text_font.render(line, True, color)
            text_rect = text_surf.get_rect(center=(w//2, y))
            surface.blit(text_surf, text_rect)
            y += 48

    def draw_hud(self, surface, player):
        # Premium Cyberpunk Cockpit HUD
        w, h = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
        
        # HP bar container border (angled cyberpunk design)
        hud_bg = pygame.Surface((340, 64), pygame.SRCALPHA)
        # semi transparent tech black background
        pygame.draw.polygon(hud_bg, (15, 20, 30, 220), [(0, 0), (320, 0), (340, 30), (300, 64), (0, 64)])
        pygame.draw.polygon(hud_bg, (0, 180, 216, 120), [(0, 0), (320, 0), (340, 30), (300, 64), (0, 64)], 2)
        surface.blit(hud_bg, (20, 20))
        
        # Dynamic HP Bar inside
        hp_pct = max(0.0, min(1.0, player.hp / PLAYER_MAX_HP))
        bar_max_w = 260
        bar_w = int(bar_max_w * hp_pct)
        
        # Back bar
        pygame.draw.polygon(surface, (60, 10, 10), [(30, 28), (30 + bar_max_w, 28), (30 + bar_max_w + 10, 42), (30 + 10, 42)])
        # Active HP bar
        if bar_w > 0:
            pygame.draw.polygon(surface, COLOR_HP_FG, [(30, 28), (30 + bar_w, 28), (30 + bar_w + 10, 42), (30 + 10, 42)])
            
        hp_text = self.text_font.render(f"KAEL VOSS  |  HP {player.hp}", True, COLOR_TEXT)
        surface.blit(hp_text, (32, 48))

        # Show Dev Mode HUD
        if settings.DEV_MODE:
            dev_surf = self.text_font.render("MODO DEV ATIVO [ SEGURE W / ESPAÇO PARA VOAR | INVENCÍVEL ]", True, (255, 255, 100))
            # Semi-transparent background for dev indicator
            dev_rect = dev_surf.get_rect(topleft=(20, 92))
            dev_bg = pygame.Surface((dev_rect.width + 20, dev_rect.height + 10), pygame.SRCALPHA)
            dev_bg.fill((10, 10, 10, 180))
            pygame.draw.rect(dev_bg, (255, 255, 0, 100), (0, 0, dev_rect.width + 20, dev_rect.height + 10), 1)
            surface.blit(dev_bg, (15, 87))
            surface.blit(dev_surf, dev_rect)
            
        # Distancia para o Beacon Telemetria
        dist_left = max(0.0, (8000 - player.rect.x) / 533.3) # 15km simulation
        dist_surf = self.subtitle_font.render(f"SINAL DE RESGATE: {dist_left:.1f} KM", True, (72, 202, 228))
        surface.blit(dist_surf, (w - dist_surf.get_width() - 30, 25))

        # Checkpoint Lore Text
        current_time = pygame.time.get_ticks()
        if self.lore_text and current_time - self.lore_timer < self.lore_duration:
            alpha = 255
            time_left = self.lore_duration - (current_time - self.lore_timer)
            if time_left < 1000:
                alpha = int(255 * (time_left / 1000))
                
            lore_surf = self.lore_font.render(self.lore_text, True, (255, 255, 200))
            lore_surf.set_alpha(alpha)
            lore_rect = lore_surf.get_rect(center=(w//2, h - 100))
            
            bg_rect = lore_rect.copy()
            bg_rect.inflate_ip(40, 20)
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height))
            bg_surf.fill((10, 15, 25))
            bg_surf.set_alpha(int(alpha * 0.75))
            pygame.draw.rect(bg_surf, (0, 180, 216), (0, 0, bg_rect.width, bg_rect.height), 1, border_radius=6)
            surface.blit(bg_surf, bg_rect)
            surface.blit(lore_surf, lore_rect)

    def show_lore(self, text):
        self.lore_text = text
        self.lore_timer = pygame.time.get_ticks()

    def draw_game_over(self, surface):
        w, h = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
        surface.fill((30, 8, 8))
        self.draw_grid_effect(surface)
        
        # Styled panel
        panel_surf = pygame.Surface((750, 420), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (15, 10, 10, 220), (0, 0, 750, 420), border_radius=12)
        pygame.draw.rect(panel_surf, (255, 50, 50, 80), (0, 0, 750, 420), 2, border_radius=12)
        surface.blit(panel_surf, panel_surf.get_rect(center=(w//2, h//2)))
        
        title = self.title_font.render("GAME OVER", True, (255, 50, 50))
        surface.blit(title, title.get_rect(center=(w//2, h//2 - 130)))
        
        msg = self.text_font.render('"A Terra recuperou mais um. O sinalizador nunca foi ativado. Ninguém veio."', True, COLOR_TEXT)
        surface.blit(msg, msg.get_rect(center=(w//2, h//2 - 40)))
        
        mouse_pos = pygame.mouse.get_pos()
        
        self.go_respawn_rect = self.draw_button(surface, "TENTAR NOVAMENTE", w//2, h//2 + 50, 360, 50, mouse_pos)
        self.go_menu_rect = self.draw_button(surface, "VOLTAR AO MENU", w//2, h//2 + 130, 360, 50, mouse_pos)

    def get_game_over_click(self, mouse_pos):
        if hasattr(self, 'go_respawn_rect') and self.go_respawn_rect.collidepoint(mouse_pos):
            return "TENTAR NOVAMENTE"
        if hasattr(self, 'go_menu_rect') and self.go_menu_rect.collidepoint(mouse_pos):
            return "VOLTAR AO MENU"
        return None

    def draw_victory(self, surface):
        w, h = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
        surface.fill((10, 35, 20))
        self.draw_grid_effect(surface)
        
        panel_surf = pygame.Surface((850, 480), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (10, 20, 15, 230), (0, 0, 850, 480), border_radius=12)
        pygame.draw.rect(panel_surf, (50, 255, 50, 80), (0, 0, 850, 480), 2, border_radius=12)
        surface.blit(panel_surf, panel_surf.get_rect(center=(w//2, h//2)))
        
        title = self.title_font.render("MISSÃO CUMPRIDA", True, (50, 255, 50))
        surface.blit(title, title.get_rect(center=(w//2, h//2 - 150)))
        
        msg1 = self.text_font.render('"O sinal foi enviado. Nas estrelas, alguém ouviu."', True, COLOR_TEXT)
        surface.blit(msg1, msg1.get_rect(center=(w//2, h//2 - 60)))
        
        msg2 = self.text_font.render('"Pela primeira vez em mil anos, um humano sobreviveu à Terra — e ela ainda não sabe o que fazer com isso."', True, COLOR_TEXT)
        surface.blit(msg2, msg2.get_rect(center=(w//2, h//2 - 10)))
        
        mouse_pos = pygame.mouse.get_pos()
        self.vic_rect = self.draw_button(surface, "VOLTAR AO MENU", w//2, h//2 + 110, 320, 50, mouse_pos)

    def draw_editor_hud(self, surface, selected_entity, selection_type, offsets_dict, save_success_timer=0):
        w, h = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
        # Draw dark border/panel at top
        panel_rect = pygame.Rect(0, 0, w, 140)
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height))
        panel_surf.fill((10, 15, 25))
        panel_surf.set_alpha(220)
        surface.blit(panel_surf, panel_rect)
        pygame.draw.line(surface, (0, 180, 216), (0, 140), (w, 140), 2)
        
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
        info_rect = pygame.Rect(w - 450, 10, 430, 120)
        pygame.draw.rect(surface, (20, 28, 42), info_rect)
        pygame.draw.rect(surface, (0, 180, 216), info_rect, 1)
        
        if selected_entity:
            name_surf = self.subtitle_font.render(f"Selecionado: {selection_type}", True, (255, 255, 100))
            surface.blit(name_surf, (w - 430, 20))
            
            x_y_surf = self.text_font.render(f"Posição Spawn: X={selected_entity.rect.x}, Y={selected_entity.rect.y}", True, COLOR_TEXT)
            surface.blit(x_y_surf, (w - 430, 55))
            
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
                surface.blit(offset_surf, (w - 430, 85))
            else:
                desc_surf = self.text_font.render("Plataforma física (sem offset de imagem)", True, (180, 180, 180))
                surface.blit(desc_surf, (w - 430, 85))
        else:
            empty_surf = self.subtitle_font.render("Nenhum item selecionado", True, (150, 150, 150))
            surface.blit(empty_surf, (w - 410, 35))
            desc_surf = self.text_font.render("Clique em um item para arrastar ou calibrar", True, (150, 150, 150))
            surface.blit(desc_surf, (w - 410, 70))
            
        # Success message overlay
        current_time = pygame.time.get_ticks()
        if save_success_timer > 0 and current_time - save_success_timer < 2500:
            success_bg = pygame.Surface((w, 50))
            success_bg.fill((10, 80, 40))
            success_bg.set_alpha(200)
            surface.blit(success_bg, (0, 142))
            
            success_surf = self.subtitle_font.render("NÍVEL E OFFSETS SALVOS COM SUCESSO EM Assets/level_data.json! 💾", True, (100, 255, 100))
            success_rect = success_surf.get_rect(center=(w//2, 167))
            surface.blit(success_surf, success_rect)
