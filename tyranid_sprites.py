import pygame
import os
import random
import math

# Colors for temporary sprite representation
TYRANID_COLORS = {
    "genestealer": (150, 50, 200),  # Purple
    "warrior": (100, 0, 150),       # Dark purple
    "gaunt": (180, 80, 180),        # Light purple
    "lictor": (120, 40, 120),       # Medium purple
    "carnifex": (80, 0, 100),       # Very dark purple
    "zoanthrope": (200, 100, 220)   # Bright purple
}

class TyranidSprite:
    """Base class for all Tyranid enemy sprites"""
    def __init__(self, x, y, width, height, tyranid_type, health, damage, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tyranid_type = tyranid_type
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.color = TYRANID_COLORS.get(tyranid_type.lower(), (150, 0, 150))
        self.is_attacking = False
        self.attack_cooldown = 1000  # milliseconds
        self.last_attack_time = 0
        self.attack_range = 50
        self.direction = "left"  # Default direction
        self.state = "idle"  # idle, moving, attacking
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.animation_time = 0
        
    def move_towards_player(self, player_x, player_y):
        """Move the Tyranid towards the player"""
        # Calculate direction vector
        dx = player_x - self.x
        dy = player_y - self.y
        
        # Update direction for sprite flipping
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        
        # Normalize the vector
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        dx = dx / distance
        dy = dy / distance
        
        # Move towards player
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # Update state
        self.state = "moving"
        
    def can_attack(self, player_x, player_y):
        """Check if the Tyranid can attack the player"""
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        current_time = pygame.time.get_ticks()
        cooldown_passed = current_time - self.last_attack_time > self.attack_cooldown
        
        return distance < self.attack_range and cooldown_passed
    
    def attack(self, player):
        """Attack the player"""
        self.last_attack_time = pygame.time.get_ticks()
        self.is_attacking = True
        self.state = "attacking"
        
        # Deal damage to player
        player.health -= self.damage
        
        # Reset attack state after a short time
        pygame.time.set_timer(pygame.USEREVENT + 1, 300)  # Reset attack state after 300ms
        
        return self.damage
    
    def take_damage(self, amount):
        """Take damage and return True if dead"""
        self.health -= amount
        return self.health <= 0
    
    def update_animation(self):
        """Update the animation frame"""
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_time > 100:  # Update animation every 100ms
            self.animation_time = current_time
            self.animation_frame += self.animation_speed
            if self.animation_frame >= 4:  # Assuming 4 frames per animation
                self.animation_frame = 0
    
    def draw(self, surface):
        """Draw the Tyranid on the surface"""
        # Temporary representation until we have sprites
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw health bar
        self.draw_health_bar(surface)
        
        # Draw attack indicator if attacking
        if self.is_attacking:
            attack_color = (255, 0, 0)  # Red
            attack_radius = 20
            attack_pos = (int(self.x + self.width/2), int(self.y + self.height/2))
            pygame.draw.circle(surface, attack_color, attack_pos, attack_radius, 2)
    
    def draw_health_bar(self, surface):
        """Draw a health bar above the Tyranid"""
        bar_width = self.width
        bar_height = 5
        x = self.x
        y = self.y - 10
        
        # Background (red)
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
        
        # Health (green)
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height), 1)


class Genestealer(TyranidSprite):
    """Ymgarl Genestealer - Fast melee attackers"""
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, "genestealer", 50, 15, 3.5)
        self.attack_range = 40
        self.attack_cooldown = 800  # Faster attacks
        # Genestealers are fast and deadly in close combat
        
    def special_ability(self, player_x, player_y):
        """Genestealers can occasionally perform a leap attack"""
        # 5% chance to leap
        if random.random() < 0.05:
            # Calculate direction vector
            dx = player_x - self.x
            dy = player_y - self.y
            
            # Normalize the vector
            distance = max(1, math.sqrt(dx*dx + dy*dy))
            dx = dx / distance
            dy = dy / distance
            
            # Leap towards player (3x normal speed)
            self.x += dx * self.speed * 3
            self.y += dy * self.speed * 3
            
            return True
        return False


class TyranidWarrior(TyranidSprite):
    """Tyranid Warrior - Balanced fighter with ranged capabilities"""
    def __init__(self, x, y):
        super().__init__(x, y, 50, 70, "warrior", 100, 20, 2)
        self.attack_range = 150  # Can attack from further away
        self.attack_cooldown = 1200
        self.ranged_attack = True
        self.projectiles = []
        
    def ranged_attack(self, player_x, player_y):
        """Perform a ranged attack by shooting bio-projectiles"""
        # Calculate direction vector
        dx = player_x - self.x
        dy = player_y - self.y
        
        # Normalize the vector
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        dx = dx / distance
        dy = dy / distance
        
        # Create a new projectile
        projectile = {
            "x": self.x + self.width/2,
            "y": self.y + self.height/2,
            "dx": dx,
            "dy": dy,
            "speed": 5,
            "damage": 10,
            "radius": 5
        }
        
        self.projectiles.append(projectile)
        
    def update_projectiles(self):
        """Update all projectiles"""
        for projectile in self.projectiles[:]:
            projectile["x"] += projectile["dx"] * projectile["speed"]
            projectile["y"] += projectile["dy"] * projectile["speed"]
            
            # Remove projectiles that are off-screen
            if (projectile["x"] < 0 or projectile["x"] > 800 or 
                projectile["y"] < 0 or projectile["y"] > 600):
                self.projectiles.remove(projectile)
                
    def draw_projectiles(self, surface):
        """Draw all projectiles"""
        for projectile in self.projectiles:
            pygame.draw.circle(
                surface, 
                (0, 255, 0),  # Green bio-projectile
                (int(projectile["x"]), int(projectile["y"])), 
                projectile["radius"]
            )
            
    def draw(self, surface):
        """Override draw to include projectiles"""
        super().draw(surface)
        self.draw_projectiles(surface)


class Gaunt(TyranidSprite):
    """Gaunt - Fast, weak melee attackers that come in hordes"""
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30, "gaunt", 30, 8, 3)
        self.attack_range = 30
        self.attack_cooldown = 1000
        # Gaunts are weak but fast and numerous


class Lictor(TyranidSprite):
    """Lictor - Stealthy ambush predator"""
    def __init__(self, x, y):
        super().__init__(x, y, 45, 70, "lictor", 80, 25, 2.5)
        self.attack_range = 60
        self.attack_cooldown = 1500
        self.is_hidden = False
        self.stealth_cooldown = 5000  # milliseconds
        self.last_stealth_time = 0
        
    def try_stealth(self):
        """Attempt to enter stealth mode"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_stealth_time > self.stealth_cooldown:
            self.is_hidden = True
            self.last_stealth_time = current_time
            # When hidden, reduce visibility
            self.color = (self.color[0], self.color[1], self.color[2], 100)  # Add transparency
            return True
        return False
    
    def ambush_attack(self, player):
        """Perform an ambush attack from stealth for extra damage"""
        if self.is_hidden:
            self.is_hidden = False
            # Reset color
            self.color = TYRANID_COLORS.get(self.tyranid_type.lower(), (150, 0, 150))
            # Deal extra damage
            damage = self.damage * 1.5
            player.health -= damage
            return damage
        return self.attack(player)
    
    def draw(self, surface):
        """Override draw to handle stealth"""
        if self.is_hidden:
            # Draw with transparency when hidden
            s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            s.fill((self.color[0], self.color[1], self.color[2], 100))
            surface.blit(s, (self.x, self.y))
            # Still draw health bar
            self.draw_health_bar(surface)
        else:
            super().draw(surface)


class Carnifex(TyranidSprite):
    """Carnifex - Heavy tank-like creature with devastating attacks"""
    def __init__(self, x, y):
        super().__init__(x, y, 80, 80, "carnifex", 200, 30, 1)
        self.attack_range = 70
        self.attack_cooldown = 2000  # Slower attacks
        
    def ground_pound(self, player_x, player_y, player):
        """Perform a ground pound attack that damages in an area"""
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # If player is within range, perform ground pound
        if distance < 100:
            # Deal damage based on distance (more damage closer)
            damage_multiplier = 1 - (distance / 100)
            damage = self.damage * damage_multiplier
            player.health -= damage
            return damage
        return 0


class Zoanthrope(TyranidSprite):
    """Zoanthrope - Psychic creature with ranged attacks"""
    def __init__(self, x, y):
        super().__init__(x, y, 40, 60, "zoanthrope", 70, 15, 1.5)
        self.attack_range = 200  # Very long range
        self.attack_cooldown = 3000  # Slow but powerful attacks
        self.psychic_blast_cooldown = 8000  # milliseconds
        self.last_psychic_blast = 0
        
    def psychic_blast(self, player_x, player_y, player):
        """Perform a powerful psychic blast attack"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_psychic_blast > self.psychic_blast_cooldown:
            self.last_psychic_blast = current_time
            
            # Calculate direction vector
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # If player is within range, perform psychic blast
            if distance < self.attack_range:
                # Deal high damage
                damage = self.damage * 2
                player.health -= damage
                return damage
        return 0
    
    def draw(self, surface):
        """Override draw to add psychic effects"""
        super().draw(surface)
        
        # Draw psychic aura
        current_time = pygame.time.get_ticks()
        if current_time - self.last_psychic_blast < 500:  # Show effect for 500ms after blast
            aura_radius = 30 + (current_time - self.last_psychic_blast) / 20
            aura_color = (200, 100, 255, 150)  # Purple with transparency
            
            s = pygame.Surface((aura_radius*2, aura_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, aura_color, (aura_radius, aura_radius), aura_radius)
            surface.blit(s, (self.x + self.width/2 - aura_radius, self.y + self.height/2 - aura_radius))


# Factory function to create different types of Tyranids
def create_tyranid(tyranid_type, x, y):
    """Create a Tyranid of the specified type"""
    if tyranid_type.lower() == "genestealer":
        return Genestealer(x, y)
    elif tyranid_type.lower() == "warrior":
        return TyranidWarrior(x, y)
    elif tyranid_type.lower() == "gaunt":
        return Gaunt(x, y)
    elif tyranid_type.lower() == "lictor":
        return Lictor(x, y)
    elif tyranid_type.lower() == "carnifex":
        return Carnifex(x, y)
    elif tyranid_type.lower() == "zoanthrope":
        return Zoanthrope(x, y)
    else:
        # Default to Gaunt if type not recognized
        return Gaunt(x, y)
