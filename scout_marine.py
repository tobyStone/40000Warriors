import pygame
import os
import math
import random

class ScoutMarine:
    """Enhanced Scout Marine class with improved mechanics"""
    def __init__(self, x, y, screen_width, screen_height):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = 50
        self.height = 70
        self.velocity = 5
        self.sprite = None
        self.sprite_flipped = None
        self.direction = "right"
        self.health = 100
        self.max_health = 100
        self.armor = 20  # Current armor value
        self.max_armor = 100  # Maximum armor value
        
        # Ammo system
        self.bolter_ammo = 30
        self.plasma_ammo = 10
        self.melta_ammo = 5
        self.max_bolter_ammo = 120
        self.max_plasma_ammo = 30
        self.max_melta_ammo = 15
        self.current_weapon = "bolter"  # Default weapon
        
        # Movement states
        self.is_moving = False
        self.movement_frame = 0
        self.movement_animation_speed = 0.2
        self.last_animation_update = 0
        self.animation_cooldown = 100  # ms
        
        # Combat attributes
        self.is_shooting = False
        self.bullets = []
        self.last_shot_time = 0
        self.shot_cooldown = 500  # milliseconds
        self.bullet_damage = 20
        self.bullet_speed = 10
        
        self.is_attacking = False
        self.attack_cooldown = 300  # milliseconds
        self.last_attack_time = 0
        self.attack_range = 60
        self.attack_damage = 25
        self.attack_frame = 0
        
        # Load sprite
        self.load_sprite("walk_right.png")
        
    def load_sprite(self, filename):
        """Load the sprite image"""
        try:
            # Get the project root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
        
            # Construct the path to the sprite with 'character' directory
            path = os.path.join(project_root,"40000Warriors", "assets", "character", filename)
        
            self.sprite = pygame.image.load(path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
            self.sprite_flipped = pygame.transform.flip(self.sprite, True, False)
        except pygame.error as e:
            print(f"Unable to load sprite: {filename}")
            print(f"Error: {e}")
            print(f"Attempted path: {path}")
            # Create a placeholder sprite
            self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.sprite.fill((0, 0, 255))  # Blue placeholder
            self.sprite_flipped = pygame.transform.flip(self.sprite, True, False)

    
    def move(self, dx, dy):
        """Move the scout with screen boundaries"""
        # Update position with screen boundaries
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check screen boundaries
        if new_x >= 0 and new_x + self.width <= self.screen_width:
            self.x = new_x
        if new_y >= 0 and new_y + self.height <= self.screen_height:
            self.y = new_y
            
        # Update direction for sprite flipping
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
            
        # Update movement state
        self.is_moving = dx != 0 or dy != 0
        
        # Update animation frame
        current_time = pygame.time.get_ticks()
        if self.is_moving and current_time - self.last_animation_update > self.animation_cooldown:
            self.last_animation_update = current_time
            self.movement_frame = (self.movement_frame + 1) % 4  # Assuming 4 frames of animation
    
    def shoot(self):
        """Shoot a bullet"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shot_cooldown:
            self.is_shooting = True
            self.last_shot_time = current_time
            
            # Create a new bullet
            direction = 1 if self.direction == "right" else -1
            bullet = {
                "x": self.x + self.width//2,
                "y": self.y + self.height//2,
                "direction": direction,
                "velocity": self.bullet_speed * direction,
                "damage": self.bullet_damage,
                "radius": 5
            }
            self.bullets.append(bullet)
            
            # Play sound effect (placeholder)
            # pygame.mixer.Sound("assets/sounds/shoot.wav").play()
            
            return True
        return False
            
    def melee_attack(self):
        """Perform a melee attack"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.is_attacking = True
            self.last_attack_time = current_time
            self.attack_frame = 0
            
            # Play sound effect (placeholder)
            # pygame.mixer.Sound("assets/sounds/melee.wav").play()
            
            return True
        return False
    
    def update_bullets(self):
        """Update bullet positions and remove bullets that are off-screen"""
        for bullet in self.bullets[:]:
            bullet["x"] += bullet["velocity"]
            if bullet["x"] < 0 or bullet["x"] > self.screen_width:
                self.bullets.remove(bullet)
    
    def update_attack_animation(self):
        """Update the attack animation"""
        if self.is_attacking:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > self.attack_cooldown:
                self.is_attacking = False
            else:
                # Update attack animation frame
                self.attack_frame = min(3, int((current_time - self.last_attack_time) / (self.attack_cooldown / 4)))
    
    def take_damage(self, amount):
        """Take damage with armor reduction"""
        # Calculate damage reduction from armor
        damage_reduction = min(amount * 0.01 * self.armor, amount * 0.8)  # Cap at 80% reduction
        actual_damage = max(1, amount - damage_reduction)  # Ensure at least 1 damage
        
        self.health -= actual_damage
        
        # Check if dead
        if self.health <= 0:
            self.health = 0
            return True  # Dead
        return False  # Still alive
    
    def heal(self, amount):
        """Heal the scout"""
        self.health = min(self.max_health, self.health + amount)
    
    def check_enemy_collision(self, enemies):
        """Check for collisions with enemies and deal melee damage if attacking"""
        if not self.is_attacking:
            return []
        
        damaged_enemies = []
        
        for enemy in enemies:
            # Calculate distance to enemy center
            player_center_x = self.x + self.width // 2
            player_center_y = self.y + self.height // 2
            enemy_center_x = enemy.x + enemy.width // 2
            enemy_center_y = enemy.y + enemy.height // 2
            
            dx = enemy_center_x - player_center_x
            dy = enemy_center_y - player_center_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Check if enemy is in attack range and in front of player
            in_range = distance < self.attack_range
            in_direction = (dx > 0 and self.direction == "right") or (dx < 0 and self.direction == "left")
            
            if in_range and in_direction:
                # Calculate damage based on distance (more damage up close)
                distance_factor = 1 - (distance / self.attack_range)
                actual_damage = self.attack_damage * distance_factor
                
                # Enemy takes damage
                if enemy.take_damage(actual_damage):
                    damaged_enemies.append(enemy)
                    
                # Visual feedback
                self.spawn_damage_number(enemy_center_x, enemy_center_y, actual_damage)
        
        return damaged_enemies
    
    def check_bullet_collisions(self, enemies):
        """Check for collisions between bullets and enemies"""
        hit_enemies = []
        
        for bullet in self.bullets[:]:
            for enemy in enemies:
                # Improved collision check using rectangles
                bullet_rect = pygame.Rect(bullet["x"] - bullet["radius"], 
                                        bullet["y"] - bullet["radius"],
                                        bullet["radius"] * 2, 
                                        bullet["radius"] * 2)
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                
                if bullet_rect.colliderect(enemy_rect):
                    # Calculate damage based on weapon type
                    damage = self.calculate_weapon_damage(bullet)
                    
                    # Enemy takes damage
                    if enemy.take_damage(damage):
                        hit_enemies.append(enemy)
                    
                    # Visual feedback
                    self.spawn_damage_number(enemy.x + enemy.width/2, 
                                          enemy.y + enemy.height/2, 
                                          damage)
                    
                    # Remove bullet
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                        self.spawn_hit_effect(bullet["x"], bullet["y"])
                    
                    break
        
        return hit_enemies
    
    def calculate_weapon_damage(self, bullet):
        """Calculate damage based on current weapon type"""
        base_damage = bullet["damage"]
        if self.current_weapon == "bolter":
            return base_damage
        elif self.current_weapon == "plasma":
            return base_damage * 1.5  # Plasma does 50% more damage
        elif self.current_weapon == "melta":
            return base_damage * 2.0  # Melta does double damage
        return base_damage
    
    def spawn_damage_number(self, x, y, damage):
        """Create a floating damage number"""
        # This is a placeholder - implement damage number system
        pass
    
    def spawn_hit_effect(self, x, y):
        """Create a hit effect at the given position"""
        # This is a placeholder - implement hit effect system
        pass
    
    def draw(self, surface):
        """Draw the scout marine"""
        # Draw the scout
        sprite_to_draw = self.sprite if self.direction == "right" else self.sprite_flipped
        
        # Apply visual effects for different states
        if self.is_attacking:
            # Flash the sprite during attack
            if self.attack_frame % 2 == 0:
                # Create a brighter version for attack flash
                bright_sprite = sprite_to_draw.copy()
                bright_sprite.fill((255, 255, 255, 100), special_flags=pygame.BLEND_ADD)
                surface.blit(bright_sprite, (self.x, self.y))
            else:
                surface.blit(sprite_to_draw, (self.x, self.y))
            
            # Draw attack arc
            if self.direction == "right":
                arc_center = (self.x + self.width, self.y + self.height // 2)
                start_angle = -math.pi/4
                end_angle = math.pi/4
            else:
                arc_center = (self.x, self.y + self.height // 2)
                start_angle = 3*math.pi/4
                end_angle = 5*math.pi/4
            
            pygame.draw.arc(surface, (255, 255, 255), 
                           (arc_center[0] - self.attack_range, 
                            arc_center[1] - self.attack_range,
                            self.attack_range * 2, 
                            self.attack_range * 2),
                           start_angle, end_angle, 3)
        else:
            surface.blit(sprite_to_draw, (self.x, self.y))
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(surface, (255, 255, 0), 
                              (int(bullet["x"]), int(bullet["y"])), 
                              bullet["radius"])
            
            # Draw bullet trail
            trail_length = 10
            trail_end_x = bullet["x"] - bullet["direction"] * trail_length
            pygame.draw.line(surface, (255, 150, 0), 
                            (bullet["x"], bullet["y"]),
                            (trail_end_x, bullet["y"]), 2)
        
        # Draw health bar
        self.draw_health_bar(surface)
    
    def draw_health_bar(self, surface):
        """Draw health bar above the scout"""
        bar_width = 50
        bar_height = 10
        x = self.x
        y = self.y - 15
        
        # Background (red)
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
        
        # Health (green)
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, health_width, bar_height))
        
        # Armor indicator (blue outline)
        armor_thickness = max(1, int(self.armor / 20))  # Scale thickness with armor value
        pygame.draw.rect(surface, (0, 0, 255), (x, y, bar_width, bar_height), armor_thickness)
    
    def update(self):
        """Update the scout's state"""
        self.update_bullets()
        self.update_attack_animation()
        
        # Reset shooting state
        if self.is_shooting and pygame.time.get_ticks() - self.last_shot_time > 100:
            self.is_shooting = False

