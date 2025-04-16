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
    "zoanthrope": (200, 100, 220),   # Bright purple
    "hive_tyrant": (200, 0, 0),      # Red
    "tyrant_guard": (150, 0, 0),     # Dark red
    "harpy": (0, 150, 150),          # Teal
    "mawloc": (100, 0, 100),         # Deep purple
    "trygon": (0, 100, 150),         # Blue
    "hive_crone": (150, 150, 0),     # Yellow
    "toxicrene": (0, 150, 0),        # Green
    "maleceptor": (200, 200, 0),     # Bright yellow
    "exocrine": (150, 100, 0),       # Orange
    "biovore": (100, 150, 0),        # Lime
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
        dx = player_x - self.x
        dy = player_y - self.y
        
        # Update direction for sprite flipping
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
        
        # Normalize vector (avoid division by zero)
        distance = max(1, math.sqrt(dx * dx + dy * dy))
        dx /= distance
        dy /= distance
        
        # Move towards player
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        self.state = "moving"

    def can_attack(self, player_x, player_y):
        """Check if the Tyranid can attack the player"""
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        current_time = pygame.time.get_ticks()
        cooldown_passed = current_time - self.last_attack_time > self.attack_cooldown
        
        return distance < self.attack_range and cooldown_passed

    def attack(self, player):
        """Attack the player"""
        self.last_attack_time = pygame.time.get_ticks()
        self.is_attacking = True
        self.state = "attacking"
        
        # Deal damage to the player
        player.health -= self.damage
        
        # Reset attack state after a short time (using timer or other logic)
        # For now, we simply return the damage inflicted.
        return self.damage

    def take_damage(self, amount):
        """Take damage and return True if dead"""
        self.health -= amount
        return self.health <= 0

    def update_animation(self):
        """Update the animation frame"""
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_time > 100:  # Update every 100ms
            self.animation_time = current_time
            self.animation_frame += self.animation_speed
            if self.animation_frame >= 4:  # Assuming 4 frames per animation loop
                self.animation_frame = 0

    def update(self):
        """Update enemy state (animation, etc.)"""
        self.update_animation()
        # (Additional per-frame logic can be added here)

    def draw(self, surface):
        """Draw the Tyranid on the surface"""
        # Temporary representation: draw a filled rectangle with the enemy's color
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        self.draw_health_bar(surface)
        # If attacking, display an attack indicator
        if self.is_attacking:
            attack_color = (255, 0, 0)  # Red for attack indicator
            attack_radius = 20
            attack_pos = (int(self.x + self.width / 2), int(self.y + self.height / 2))
            pygame.draw.circle(surface, attack_color, attack_pos, attack_radius, 2)

    def draw_health_bar(self, surface):
        """Draw a health bar above the Tyranid"""
        bar_width = self.width
        bar_height = 5
        x = self.x
        y = self.y - 10
        # Background bar (red)
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
        # Health amount (green)
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, health_width, bar_height))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height), 1)

class Genestealer(TyranidSprite):
    """Ymgarl Genestealer - Fast melee attackers"""
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, "genestealer", 50, 15, 3.5)
        self.attack_range = 40
        self.attack_cooldown = 800  # Faster attacks
        # Genestealers are fast and deadly in close combat
        
    def update(self):
        super().update()
        # You might add special abilities here if needed
        
    def special_ability(self, player_x, player_y):
        """Occasionally perform a leap attack"""
        if random.random() < 0.05:  # 5% chance to leap
            dx = player_x - self.x
            dy = player_y - self.y
            distance = max(1, math.sqrt(dx * dx + dy * dy))
            dx /= distance
            dy /= distance
            self.x += dx * self.speed * 3
            self.y += dy * self.speed * 3
            return True
        return False

class TyranidWarrior(TyranidSprite):
    """Tyranid Warrior - Balanced fighter with ranged capabilities"""
    def __init__(self, x, y):
        super().__init__(x, y, 50, 70, "warrior", 100, 20, 2)
        self.attack_range = 150  # Longer range
        self.attack_cooldown = 1200
        self.ranged_attack_enabled = True
        self.projectiles = []

    def ranged_attack(self, player_x, player_y):
        """Perform a ranged attack by shooting bio-projectiles"""
        dx = player_x - self.x
        dy = player_y - self.y
        distance = max(1, math.sqrt(dx * dx + dy * dy))
        dx /= distance
        dy /= distance
        projectile = {
            "x": self.x + self.width / 2,
            "y": self.y + self.height / 2,
            "dx": dx,
            "dy": dy,
            "speed": 5,
            "damage": 10,
            "radius": 5
        }
        self.projectiles.append(projectile)
    
    def update_projectiles(self):
        """Update positions of bio-projectiles"""
        for projectile in self.projectiles[:]:
            projectile["x"] += projectile["dx"] * projectile["speed"]
            projectile["y"] += projectile["dy"] * projectile["speed"]
            if (projectile["x"] < 0 or projectile["x"] > 800 or
                projectile["y"] < 0 or projectile["y"] > 600):
                self.projectiles.remove(projectile)
    
    def draw_projectiles(self, surface):
        """Draw projectiles on the surface"""
        for projectile in self.projectiles:
            pygame.draw.circle(surface, (0, 255, 0),
                               (int(projectile["x"]), int(projectile["y"])),
                               projectile["radius"])
    
    def update(self):
        """Update warrior state, including projectiles, then base animations"""
        self.update_projectiles()
        super().update()
    
    def draw(self, surface):
        """Draw the warrior and its projectiles"""
        super().draw(surface)
        self.draw_projectiles(surface)

class Gaunt(TyranidSprite):
    """Gaunt - Fast, weak melee attackers that come in hordes"""
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30, "gaunt", 30, 8, 3)
        self.attack_range = 30
        self.attack_cooldown = 1000

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
            # Optionally modify sprite transparency here
            return True
        return False
    
    def ambush_attack(self, player):
        """Perform an ambush attack from stealth for extra damage"""
        if self.is_hidden:
            self.is_hidden = False
            damage = self.damage * 1.5
            player.health -= damage
            return damage
        return self.attack(player)
    
    def draw(self, surface):
        """Draw Lictor with stealth effect if hidden"""
        if self.is_hidden:
            s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            s.fill((self.color[0], self.color[1], self.color[2], 100))
            surface.blit(s, (self.x, self.y))
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
        """Perform a ground pound attack dealing area damage"""
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < 100:
            damage_multiplier = 1 - (distance / 100)
            damage = self.damage * damage_multiplier
            player.health -= damage
            return damage
        return 0

class Zoanthrope(TyranidSprite):
    """Zoanthrope - Psychic creature with ranged attacks"""
    def __init__(self, x, y):
        super().__init__(x, y, 40, 60, "zoanthrope", 70, 15, 1.5)
        self.attack_range = 200
        self.attack_cooldown = 3000
        self.psychic_blast_cooldown = 8000  # milliseconds
        self.last_psychic_blast = 0
        
    def psychic_blast(self, player_x, player_y, player):
        """Perform a powerful psychic blast attack"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_psychic_blast > self.psychic_blast_cooldown:
            self.last_psychic_blast = current_time
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < self.attack_range:
                damage = self.damage * 2
                player.health -= damage
                return damage
        return 0
    
    def draw(self, surface):
        """Override draw to add psychic effects"""
        super().draw(surface)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_psychic_blast < 500:
            aura_radius = 30 + (current_time - self.last_psychic_blast) / 20
            aura_color = (200, 100, 255, 150)
            s = pygame.Surface((aura_radius*2, aura_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, aura_color, (aura_radius, aura_radius), aura_radius)
            surface.blit(s, (self.x + self.width/2 - aura_radius, self.y + self.height/2 - aura_radius))

class HiveTyrant(TyranidSprite):
    """Elite Tyranid commander with powerful melee and psychic abilities"""
    def __init__(self, x, y):
        super().__init__(x, y, 80, 80, "hive_tyrant", 300, 40, 3)
        self.wings_angle = 0
        self.wings_speed = 0.1
        self.psychic_power = 100
        self.max_psychic_power = 100
        self.psychic_cooldown = 3000  # milliseconds
        self.last_psychic_time = 0

    def update(self):
        super().update()
        # Animate wings
        self.wings_angle += self.wings_speed
        if self.wings_angle > 2 * math.pi:
            self.wings_angle = 0

    def psychic_scream(self, player):
        """Psychic ability that stuns and damages the player"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_psychic_time > self.psychic_cooldown:
            self.last_psychic_time = current_time
            # Create psychic wave effect
            return True
        return False

    def draw(self, surface):
        # Draw main body
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw wings
        wing_length = 40
        for side in [-1, 1]:
            wing_x = self.x + self.width // 2
            wing_y = self.y + self.height // 2
            end_x = wing_x + math.cos(self.wings_angle + side * math.pi/2) * wing_length
            end_y = wing_y + math.sin(self.wings_angle + side * math.pi/2) * wing_length
            pygame.draw.line(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2),
                           (wing_x, wing_y), (end_x, end_y), 5)
        
        # Draw psychic power bar
        power_bar_width = 60
        power_bar_height = 5
        pygame.draw.rect(surface, (100, 100, 100),
                        (self.x + (self.width - power_bar_width)//2,
                         self.y - 15,
                         power_bar_width,
                         power_bar_height))
        pygame.draw.rect(surface, (200, 200, 0),
                        (self.x + (self.width - power_bar_width)//2,
                         self.y - 15,
                         power_bar_width * (self.psychic_power / self.max_psychic_power),
                         power_bar_height))
        
        self.draw_health_bar(surface)

class Harpy(TyranidSprite):
    """Flying Tyranid with ranged attacks and swooping abilities"""
    def __init__(self, x, y):
        super().__init__(x, y, 60, 60, "harpy", 150, 25, 5)
        self.is_flying = True
        self.swoop_cooldown = 5000  # milliseconds
        self.last_swoop_time = 0
        self.swoop_target = None
        self.swoop_speed = 10
        self.wing_angle = 0
        self.wing_speed = 0.2

    def update(self):
        super().update()
        # Animate wings
        self.wing_angle += self.wing_speed
        if self.wing_angle > 2 * math.pi:
            self.wing_angle = 0

    def swoop_attack(self, player_x, player_y):
        """Swoop down at the player for increased damage"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_swoop_time > self.swoop_cooldown:
            self.last_swoop_time = current_time
            self.swoop_target = (player_x, player_y)
            self.is_flying = False
            return True
        return False

    def draw(self, surface):
        # Draw body
        pygame.draw.ellipse(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw wings
        wing_length = 50
        for side in [-1, 1]:
            wing_x = self.x + self.width // 2
            wing_y = self.y + self.height // 2
            end_x = wing_x + math.cos(self.wing_angle + side * math.pi/2) * wing_length
            end_y = wing_y + math.sin(self.wing_angle + side * math.pi/2) * wing_length
            pygame.draw.line(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2),
                           (wing_x, wing_y), (end_x, end_y), 4)
        
        self.draw_health_bar(surface)

class Mawloc(TyranidSprite):
    """Burrowing Tyranid that can emerge from the ground"""
    def __init__(self, x, y):
        super().__init__(x, y, 100, 100, "mawloc", 400, 50, 2)
        self.is_burrowed = True
        self.burrow_cooldown = 8000  # milliseconds
        self.last_burrow_time = 0
        self.emergence_time = 0
        self.emergence_duration = 1000  # milliseconds

    def update(self):
        super().update()
        if not self.is_burrowed:
            current_time = pygame.time.get_ticks()
            if current_time - self.emergence_time > self.emergence_duration:
                self.is_burrowed = True
                self.last_burrow_time = current_time

    def emerge(self, target_x, target_y):
        """Emerge from the ground at target location"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_burrow_time > self.burrow_cooldown:
            self.x = target_x
            self.y = target_y
            self.is_burrowed = False
            self.emergence_time = current_time
            return True
        return False

    def draw(self, surface):
        if not self.is_burrowed:
            # Draw emerging animation
            progress = min(1.0, (pygame.time.get_ticks() - self.emergence_time) / self.emergence_duration)
            height = int(self.height * progress)
            pygame.draw.ellipse(surface, self.color,
                              (self.x, self.y + self.height - height,
                               self.width, height))
            
            # Draw mandibles
            mandible_length = 30
            for side in [-1, 1]:
                start_x = self.x + self.width // 2
                start_y = self.y + self.height - height
                end_x = start_x + side * mandible_length
                end_y = start_y - 20
                pygame.draw.line(surface, (self.color[0]//2, self.color[1]//2, self.color[2]//2),
                               (start_x, start_y), (end_x, end_y), 5)
        
        if not self.is_burrowed:
            self.draw_health_bar(surface)

def create_tyranid(tyranid_type, x, y):
    """Factory function to create Tyranid enemies"""
    tyranid_classes = {
        "genestealer": Genestealer,
        "warrior": TyranidWarrior,
        "gaunt": Gaunt,
        "lictor": Lictor,
        "carnifex": Carnifex,
        "zoanthrope": Zoanthrope,
        "hive_tyrant": HiveTyrant,
        "harpy": Harpy,
        "mawloc": Mawloc
    }
    
    tyranid_class = tyranid_classes.get(tyranid_type.lower())
    if tyranid_class:
        return tyranid_class(x, y)
    return None

# Expose the API for importers
__all__ = ["TyranidSprite", "Genestealer", "TyranidWarrior", "Gaunt", "Lictor", "Carnifex", "Zoanthrope", "create_tyranid"]
