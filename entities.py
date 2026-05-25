import pygame
import math
import time
from settings import *
from assets import IMAGES, SOUNDS

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.hp = 100
        self.is_dead = False
        self.facing_right = True
        self.knockback_timer = 0

    def apply_gravity(self):
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

    def take_damage(self, amount, knockback_x=0):
        import settings
        if settings.DEV_MODE and self.__class__.__name__ == 'Player':
            return # Invincible in Dev Mode
        self.hp -= amount
        if knockback_x != 0:
            self.vel_x = knockback_x
            self.knockback_timer = 15  # 15 frames of knockback (~250ms at 60fps)
        self.vel_y -= 3  # slight popup
        # Play damage sound safely
        if self.__class__.__name__ == 'Player':
            SOUNDS['player_damage'].play()
        else:
            SOUNDS['enemy_damage'].play()
        if self.hp <= 0:
            self.die()

    def die(self):
        self.is_dead = True
        self.kill()

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 60, COLOR_PLAYER)
        self.hp = PLAYER_MAX_HP
        self.on_ground = False
        self.last_attack_time = 0
        self.is_attacking = False
        self.attack_duration = 100 # ms
        self.attack_rect = None
        self.coyote_timer = 0
        self.jump_buffer_timer = 0

    def update(self, keys, mouse_buttons, platforms, enemies):
        if self.is_dead:
            return

        # Update Coyote Time and Jump Buffer timers
        if self.on_ground:
            self.coyote_timer = 8  # 8 frames of tolerance
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1

        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        # If under knockback, ignore inputs and apply friction
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
            self.vel_x *= 0.85
            if abs(self.vel_x) < 0.2:
                self.vel_x = 0
        else:
            # Movement
            speed = PLAYER_RUN_SPEED if keys[pygame.K_LSHIFT] else PLAYER_SPEED
            
            # Friction
            self.vel_x *= 0.8
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0
            
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.vel_x -= speed * 0.2
                self.facing_right = False
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.vel_x += speed * 0.2
                self.facing_right = True

        # Register jump command (Jump Buffering)
        if keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            self.jump_buffer_timer = 6  # Save command for 6 frames

        import settings
        if settings.DEV_MODE:
            if keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]:
                self.vel_y = -8  # Flight in Dev Mode
                self.on_ground = False
        else:
            if self.jump_buffer_timer > 0 and (self.on_ground or self.coyote_timer > 0):
                self.vel_y = PLAYER_JUMP_FORCE
                self.on_ground = False
                self.coyote_timer = 0
                self.jump_buffer_timer = 0
                SOUNDS['jump'].play()

        self.apply_gravity()
        
        # Attack logic
        current_time = pygame.time.get_ticks()
        
        # Reset attack visual
        if self.is_attacking and current_time - self.last_attack_time > self.attack_duration:
            self.is_attacking = False
            self.attack_rect = None

        # Process attack input
        if mouse_buttons[0] or mouse_buttons[2]: # Left or Right click
            is_heavy = mouse_buttons[2]
            cooldown = HEAVY_ATTACK_COOLDOWN if is_heavy else LIGHT_ATTACK_COOLDOWN
            
            if current_time - self.last_attack_time >= cooldown:
                self.attack(is_heavy, enemies)
                self.last_attack_time = current_time

        # Movement and Collision
        self.rect.x += int(self.vel_x)
        self.check_collisions_x(platforms)
        self.check_enemy_collisions_x(enemies)
        
        self.rect.y += int(self.vel_y)
        self.check_collisions_y(platforms)
        
        # Death pit
        if self.rect.y > DEATH_Y:
            self.take_damage(9999)

    def attack(self, is_heavy, enemies):
        self.is_attacking = True
        
        damage = HEAVY_ATTACK_DAMAGE if is_heavy else LIGHT_ATTACK_DAMAGE
        attack_range = HEAVY_ATTACK_RANGE if is_heavy else LIGHT_ATTACK_RANGE
        
        # Play attack sound safely
        if is_heavy:
            SOUNDS['heavy_attack'].play()
        else:
            SOUNDS['light_attack'].play()
        
        # Create hitbox
        hitbox_width = attack_range
        hitbox_height = 40
        
        if self.facing_right:
            self.attack_rect = pygame.Rect(self.rect.right, self.rect.centery - hitbox_height//2, hitbox_width, hitbox_height)
        else:
            self.attack_rect = pygame.Rect(self.rect.left - hitbox_width, self.rect.centery - hitbox_height//2, hitbox_width, hitbox_height)
            
        # Check enemy collisions
        for enemy in enemies:
            if self.attack_rect.colliderect(enemy.rect):
                kb = 10 if self.facing_right else -10
                if is_heavy: kb *= 1.5
                enemy.take_damage(damage, kb)

    def check_collisions_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.rect.right = p.rect.left
                elif self.vel_x < 0:
                    self.rect.left = p.rect.right
                self.vel_x = 0

    def check_enemy_collisions_x(self, enemies):
        for enemy in enemies:
            # Only collide physically with live ground enemies (Monkey)
            if hasattr(enemy, 'patrol_anchor') and not enemy.is_dead:
                if self.rect.colliderect(enemy.rect):
                    if self.vel_x > 0 or (enemy.vel_x < 0 and self.rect.centerx < enemy.rect.centerx):
                        self.rect.right = enemy.rect.left
                    elif self.vel_x < 0 or (enemy.vel_x > 0 and self.rect.centerx > enemy.rect.centerx):
                        self.rect.left = enemy.rect.right
                    self.vel_x = 0

    def check_collisions_y(self, platforms):
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0
                    
        # Double check if standing exactly on any platform to prevent frame-by-frame on_ground flickering
        if not self.on_ground:
            probe = self.rect.copy()
            probe.y += 1
            for p in platforms:
                if probe.colliderect(p.rect):
                    self.on_ground = True
                    break

    def draw(self, surface, camera_offset_x):
        from assets import GLOBAL_OFFSETS
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset_x
        # Touches the grass top perfectly
        draw_rect.y += GLOBAL_OFFSETS.get('player', 0)
        
        # Determine image
        if self.is_attacking:
            if self.attack_rect and self.attack_rect.width == HEAVY_ATTACK_RANGE:
                img = IMAGES['player_strong_attack']
            else:
                img = IMAGES['player_normal_attack']
        elif not self.on_ground:
            img = IMAGES['player_stand']
        elif self.vel_x != 0:
            # Animation speed proportional to real velocity
            anim_speed = 200 if abs(self.vel_x) > PLAYER_SPEED + 0.5 else 400
            if pygame.time.get_ticks() % anim_speed < (anim_speed // 2):
                img = IMAGES['player_walk_1']
            else:
                img = IMAGES['player_walk_2']
        else:
            img = IMAGES['player_stand']
            
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
            
        surface.blit(img, draw_rect)
        
        # Draw attack effect (red box) just for visual cue if needed
        # if self.is_attacking and self.attack_rect:
        #     atk_draw_rect = self.attack_rect.copy()
        #     atk_draw_rect.x -= camera_offset_x
        #     color = (255, 50, 50) if self.attack_rect.width == HEAVY_ATTACK_RANGE else (200, 200, 200)
        #     pygame.draw.rect(surface, color, atk_draw_rect, 2) # outline only


class Monkey(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, COLOR_ENEMY_MONKEY)
        self.hp = MONKEY_HP
        self.patrol_anchor = x
        self.patrol_distance = 150
        self.vel_x = MONKEY_SPEED
        self.facing_right = True
        self.last_attack_time = 0
        self.image = IMAGES['monkey_stand']
        self.collided_this_frame = False

    def update(self, player, platforms):
        if self.is_dead:
            return
            
        self.apply_gravity()
        
        # Save player collision state before resolution
        self.collided_this_frame = self.rect.colliderect(player.rect)

        # If under knockback, ignore AI and apply horizontal friction
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
            self.vel_x *= 0.85
            if abs(self.vel_x) < 0.2:
                self.vel_x = 0
        else:
            # Distance to player
            dist_x = player.rect.centerx - self.rect.centerx
            dist_y = player.rect.centery - self.rect.centery
            distance = math.hypot(dist_x, dist_y)
            
            # AI logic
            is_chasing = False
            if distance < 120 and abs(dist_y) < 80:
                # Chase
                is_chasing = True
                speed = MONKEY_CHASE_SPEED
                if dist_x > 0:
                    self.vel_x = speed
                    self.facing_right = True
                else:
                    self.vel_x = -speed
                    self.facing_right = False
            else:
                # Patrol
                if self.rect.x > self.patrol_anchor + self.patrol_distance:
                    self.vel_x = -MONKEY_SPEED
                    self.facing_right = False
                elif self.rect.x < self.patrol_anchor - self.patrol_distance:
                    self.vel_x = MONKEY_SPEED
                    self.facing_right = True

            # Ledge detection to prevent falling
            if self.vel_x != 0:
                probe_x = self.rect.right + 5 if self.vel_x > 0 else self.rect.left - 5
                probe_rect = pygame.Rect(probe_x, self.rect.bottom + 5, 2, 2)
                has_ground = any(probe_rect.colliderect(p.rect) for p in platforms)
                
                if not has_ground:
                    if is_chasing:
                        self.vel_x = 0
                    else:
                        self.vel_x *= -1
                        self.facing_right = self.vel_x > 0
                        self.patrol_anchor = self.rect.x

        # Apply movement
        self.rect.x += self.vel_x
        self.check_collisions_x(platforms)
        self.check_player_collision_x(player)
        
        self.rect.y += int(self.vel_y)
        self.check_collisions_y(platforms)
        
        # Fall death
        if self.rect.y > DEATH_Y:
            self.die()

        # Damage player
        if self.collided_this_frame:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > 1000: # 1 sec cooldown
                player.take_damage(MONKEY_DAMAGE, 10 if self.facing_right else -10)
                self.last_attack_time = current_time
                SOUNDS['monkey_attack'].play()

    def check_collisions_x(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.rect.right = p.rect.left
                    self.vel_x = -abs(self.vel_x) # Reverse direction
                elif self.vel_x < 0:
                    self.rect.left = p.rect.right
                    self.vel_x = abs(self.vel_x)

    def check_player_collision_x(self, player):
        if not player.is_dead and self.rect.colliderect(player.rect):
            self.collided_this_frame = True
            if self.vel_x > 0:
                self.rect.right = player.rect.left
                # Stop movement if chasing, or pause
                self.vel_x = 0
            elif self.vel_x < 0:
                self.rect.left = player.rect.right
                self.vel_x = 0

    def check_collisions_y(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.rect.bottom = p.rect.top
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = p.rect.bottom
                    self.vel_y = 0

    def draw(self, surface, camera_offset_x):
        from assets import GLOBAL_OFFSETS
        draw_rect = self.rect.copy()
        draw_rect.x -= camera_offset_x
        
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time < 300:
            img = IMAGES['monkey_attack']
            # Corrected to subtract and lift the sprite to prevent sinking in the ground
            draw_rect.x -= 7
            draw_rect.y += GLOBAL_OFFSETS.get('monkey_attack', -14)
        elif self.vel_x != 0:
            if current_time % 400 < 200:
                img = IMAGES['monkey_walk_1']
            else:
                img = IMAGES['monkey_walk_2']
            # Corrected to subtract and lift the sprite
            draw_rect.x -= 5
            draw_rect.y += GLOBAL_OFFSETS.get('monkey_walk', -10)
        else:
            img = IMAGES['monkey_stand']
            # Corrected to subtract and lift the sprite
            draw_rect.x -= 7
            draw_rect.y += GLOBAL_OFFSETS.get('monkey_stand', -14)
            
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
            
        surface.blit(img, draw_rect)

class Bird(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30, COLOR_ENEMY_BIRD)
        self.hp = BIRD_HP
        self.patrol_anchor_x = x
        self.patrol_anchor_y = y
        self.patrol_distance = 200
        self.vel_x = BIRD_SPEED
        self.facing_right = True
        self.last_attack_time = 0
        self.state = "patrol" # patrol, swoop, return
        self.image = IMAGES['bird_fly_1']
        self.collided_this_frame = False

    def apply_gravity(self):
        pass # Birds don't have gravity

    def update(self, player, platforms):
        if self.is_dead:
            return
            
        # Save player collision state before resolution
        self.collided_this_frame = self.rect.colliderect(player.rect)

        # If bird is under knockback, suspend default AI and apply friction to vector
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
            self.vel_x *= 0.85
            self.rect.x += int(self.vel_x)
            if abs(self.vel_x) < 0.2:
                self.vel_x = 0
        else:
            dist_x = player.rect.centerx - self.rect.centerx
            dist_y = player.rect.centery - self.rect.centery
            distance = math.hypot(dist_x, dist_y)

            if self.state == "patrol":
                if distance < 250 and player.rect.y > self.rect.y:
                    self.state = "swoop"
                    SOUNDS['bird_attack'].play()
                else:
                    if self.rect.x > self.patrol_anchor_x + self.patrol_distance:
                        self.vel_x = -BIRD_SPEED
                    elif self.rect.x < self.patrol_anchor_x - self.patrol_distance:
                        self.vel_x = BIRD_SPEED
                    
                    self.rect.x += self.vel_x
                    self.facing_right = self.vel_x > 0
                    # gentle hover
                    self.rect.y = self.patrol_anchor_y + math.sin(pygame.time.get_ticks() * 0.005) * 10
                    
            elif self.state == "swoop":
                # Move towards player
                angle = math.atan2(dist_y, dist_x)
                move_x = int(math.cos(angle) * BIRD_SWOOP_SPEED)
                self.rect.x += move_x
                self.rect.y += int(math.sin(angle) * BIRD_SWOOP_SPEED)
                self.facing_right = dist_x > 0
                
                if distance > 400 or self.rect.y > player.rect.bottom + 50:
                    self.state = "return"
                    
            elif self.state == "return":
                dist_to_anchor = math.hypot(self.patrol_anchor_x - self.rect.x, self.patrol_anchor_y - self.rect.y)
                if dist_to_anchor < 10:
                    self.state = "patrol"
                else:
                    angle = math.atan2(self.patrol_anchor_y - self.rect.y, self.patrol_anchor_x - self.rect.x)
                    move_x = int(math.cos(angle) * BIRD_SPEED)
                    self.rect.x += move_x
                    self.rect.y += int(math.sin(angle) * BIRD_SPEED)
                    self.facing_right = (self.patrol_anchor_x - self.rect.x) > 0

        # Solid dynamic physics: prevent bird from overlapping inside player
        self.check_player_collision_x(player)

        # Damage player
        if self.collided_this_frame:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > 1000:
                player.take_damage(BIRD_DAMAGE, 5 if self.facing_right else -5)
                self.last_attack_time = current_time

    def check_player_collision_x(self, player):
        if not player.is_dead and self.rect.colliderect(player.rect):
            self.collided_this_frame = True
            overlap_x = min(self.rect.right, player.rect.right) - max(self.rect.left, player.rect.left)
            overlap_y = min(self.rect.bottom, player.rect.bottom) - max(self.rect.top, player.rect.top)
            if overlap_x > 0 and overlap_y > 0:
                if overlap_x < overlap_y:
                    if self.rect.centerx < player.rect.centerx:
                        self.rect.right = player.rect.left
                    else:
                        self.rect.left = player.rect.right
                else:
                    if self.rect.centery < player.rect.centery:
                        self.rect.bottom = player.rect.top
                    else:
                        self.rect.top = player.rect.bottom
                self.state = "return" # bounce back immediately

    def draw(self, surface, camera_offset_x):
        from assets import GLOBAL_OFFSETS
        # Draw 40x40 sprite centered over 30x30 hitbox with customizable offset
        draw_rect = pygame.Rect(self.rect.x - 5 - camera_offset_x, self.rect.y + GLOBAL_OFFSETS.get('bird', -5), 40, 40)
        
        # Wing flap animation
        if pygame.time.get_ticks() % 300 < 150:
            img = IMAGES['bird_fly_1']
        else:
            img = IMAGES['bird_fly_2']
            
        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
            
        surface.blit(img, draw_rect)
