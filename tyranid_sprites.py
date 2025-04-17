import pygame
import os
import random
import math
import traceback

# Colors for temporary sprite representation
TYRANID_COLORS = {
    "genestealer": (150, 50, 200),  # Purple
    "warrior": (100, 0, 150),       # Dark purple
    "gaunt": (180, 80, 180),        # Light purple
    "lictor": (120, 40, 120),       # Medium purple
    "carnifex": (80, 0, 100),       # Very dark purple
    "zoanthrope": (200, 100, 220),  # Bright purple
    "hive_tyrant": (200, 0, 0),     # Red
#    "tyrant_guard": (150, 0, 0),    # Dark red
#    "harpy": (0, 150, 150),         # Teal
    "mawloc": (100, 0, 100),        # Deep purple
    "trygon": (0, 100, 150),        # Blue
    "hive_crone": (150, 150, 0),    # Yellow
    "toxicrene": (0, 150, 0),       # Green
    "maleceptor": (200, 200, 0),    # Bright yellow
    "exocrine": (150, 100, 0),      # Orange
    "biovore": (100, 150, 0),       # Lime
}

class TyranidSprite:
    """Base class for all Tyranid enemy sprites"""
    def __init__(self, x, y, width, height, tyranid_type, health, damage, speed):
        """Initialize a new Tyranid enemy with all parameters passed in."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tyranid_type = tyranid_type

        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed

        self.is_alive = True
        self.last_movement = (0, 0)

        # Animation variables
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.2  # Time between frame changes

        # Debug mode
        self.debug_mode = False

        # Sprites
        self.sprite = None
        self.frames = None
        self.frames_flipped = None

        # Attack defaults (overridden in subclasses)
        self.attack_range = 0
        self.attack_cooldown = 0
        self.last_attack_time = 0
        self.is_attacking = False

        print(f"Initializing Tyranid of type {tyranid_type} at position ({x}, {y})")
        self.load_sprites()

    def load_sprites(self):
        """Load the appropriate sprites based on tyranid type."""
        # Determine project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)

        # 1) Try the 'character' folder first
        char_path = os.path.join(
            project_root,
            "40000Warriors", "assets", "character",
            f"{self.tyranid_type}.png"
        )
        print(f"Loading Tyranid sprite from (character): {char_path}")
        if os.path.exists(char_path):
            # Load and scale to hit‐box immediately
            raw = pygame.image.load(char_path).convert_alpha()
            sheet = pygame.transform.smoothscale(raw, (self.width, self.height))
            self.frames = [sheet]
            self.frames_flipped = [pygame.transform.flip(sheet, True, False)]
            self.sprite = sheet
            print(f"  → loaded & scaled to {self.width}×{self.height}")
            return

        # 2) Fallback to the 'enemies' folder
        enemy_path = os.path.join(
            project_root,
            "assets", "enemies",
            f"{self.tyranid_type}.png"
        )
        print(f"Character sprite not found, falling back to: {enemy_path}")
        if not os.path.exists(enemy_path):
            # Ultimate fallback: magenta box
            print(f"ERROR: No sprite found for {self.tyranid_type} in character or enemies")
            placeholder = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            placeholder.fill((255, 0, 255))
            pygame.draw.rect(placeholder, (0, 0, 0), placeholder.get_rect(), 2)
            self.frames = [placeholder]
            self.frames_flipped = [pygame.transform.flip(placeholder, True, False)]
            self.sprite = placeholder
            return

        # Load sprite sheet from enemies folder
        sprite_sheet = pygame.image.load(enemy_path).convert_alpha()

        # 3) Single‐frame vs multi‐frame logic (unchanged)
        if sprite_sheet.get_width() <= self.width:
            # single‐frame image
            img = pygame.transform.scale(sprite_sheet, (self.width, self.height))
            self.frames = [img]
            self.frames_flipped = [pygame.transform.flip(img, True, False)]
        else:
            # extract animation frames
            frame_count = sprite_sheet.get_width() // self.width
            self.frames = []
            self.frames_flipped = []
            for i in range(frame_count):
                frame = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                frame.blit(
                    sprite_sheet,
                    (0, 0),
                    (i * self.width, 0, self.width, self.height)
                )
                if (frame.get_width(), frame.get_height()) != (self.width, self.height):
                    frame = pygame.transform.scale(frame, (self.width, self.height))
                self.frames.append(frame)
                self.frames_flipped.append(pygame.transform.flip(frame, True, False))

        # Finalize
        self.sprite = self.frames[0]
        print(f"Successfully loaded {len(self.frames)} frame(s) for {self.tyranid_type}")

    def move_towards_player(self, player_x, player_y):
        """Move towards the player"""
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance > 0:
            dx = (dx / distance) * self.speed
            dy = (dy / distance) * self.speed
            self.last_movement = (dx, dy)
            self.x += dx
            self.y += dy
            if dx > 0:
                self.direction = "right"
            elif dx < 0:
                self.direction = "left"
            if abs(dx) > 0.1 or abs(dy) > 0.1:
                self.current_state = "moving"
            else:
                self.current_state = "idle"
        else:
            self.current_state = "idle"
            self.last_movement = (0, 0)

    def can_attack(self, player_x, player_y):
        """Check if the Tyranid can attack the player"""
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        current_time = pygame.time.get_ticks()
        cooldown_passed = current_time - self.last_attack_time > self.attack_cooldown
        return distance < self.attack_range and cooldown_passed

    def attack(self, target):
        """Perform an attack"""
        self.is_attacking = True
        self.current_state = "attacking"
        # implement attack logic here

    def take_damage(self, amount):
        """Take damage and return True if dead"""
        self.health -= amount
        return self.health <= 0

    def update_animation(self):
        """Update the animation frame"""
        if not self.frames:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_time > 100:
            self.animation_time = current_time
            if self.current_state != "idle":
                self.current_frame = (self.current_frame + 1) % 4
            else:
                self.current_frame = 0
            try:
                frames = self.frames_flipped if self.direction == "left" else self.frames
                self.sprite = frames[self.current_frame]
                print(f"Animation updated: {self.current_state}, frame {self.current_frame}, direction {self.direction}")
            except Exception as e:
                print(f"Error updating animation: {e}")
                print(f"State: {self.current_state}, Frame: {self.current_frame}, Dir: {self.direction}")

    def update(self, delta_time=1/60):
        """Update the tyranid state"""
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        if self.is_attacking and self.current_frame == 3:
            self.is_attacking = False
            self.current_state = "idle"

    def draw(self, surface):
        """Draw the tyranid on the given surface"""
        if self.sprite:
            if self.last_movement[0] > 0:
                current_sprite = self.frames_flipped[self.current_frame]
            else:
                current_sprite = self.frames[self.current_frame]
            surface.blit(current_sprite, (self.x, self.y))
        else:
            pygame.draw.rect(surface, (255, 0, 255), (self.x, self.y, self.width, self.height))
        health_bar_width = int((self.health / self.max_health) * self.width)
        pygame.draw.rect(surface, (255, 0, 0), (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(surface, (0, 255, 0), (self.x, self.y - 10, health_bar_width, 5))
        if self.debug_mode:
            pygame.draw.rect(surface, (255, 0, 0), self.get_rect(), 1)

    def draw_health_bar(self, surface):
        """Draw a health bar above the Tyranid"""
        bar_width = self.width
        bar_height = 5
        x = self.x
        y = self.y - 10
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, health_width, bar_height))
        pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height), 1)

    def load_tyranid_sprite(self, sprite_name):
        """Load a sprite for the Tyranid"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            path = os.path.join(project_root, "40000Warriors", "assets", sprite_name)
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load Tyranid sprite: {sprite_name}")
            print(f"Error: {e}")
            print(f"Attempted path: {path}")
            surface = pygame.Surface((64, 64), pygame.SRCALPHA)
            surface.fill((255, 0, 0))
            pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
            return surface

# Subclasses
class Genestealer(TyranidSprite):
    """Ymgarl Genestealer - Fast melee attackers"""
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, "genestealer", 50, 15, 3.5)
        self.attack_range = 40
        self.attack_cooldown = 800

class TyranidWarrior(TyranidSprite):
    """Tyranid Warrior - Balanced fighter with ranged capabilities"""
    def __init__(self, x, y):
        super().__init__(x, y, 50, 70, "warrior", 100, 20, 2)
        self.attack_range = 150
        self.attack_cooldown = 1200
        self.ranged_attack_enabled = True
        self.projectiles = []

    def ranged_attack(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = max(1, math.sqrt(dx*dx + dy*dy))
        dx /= distance
        dy /= distance
        projectile = {"x": self.x + self.width/2, "y": self.y + self.height/2,
                      "dx": dx, "dy": dy, "speed": 5, "damage": 10, "radius": 5}
        self.projectiles.append(projectile)

    def update_projectiles(self):
        for proj in self.projectiles[:]:
            proj["x"] += proj["dx"] * proj["speed"]
            proj["y"] += proj["dy"] * proj["speed"]
            if proj["x"] < 0 or proj["x"] > 800 or proj["y"] < 0 or proj["y"] > 600:
                self.projectiles.remove(proj)

    def draw_projectiles(self, surface):
        for proj in self.projectiles:
            pygame.draw.circle(surface, (0, 255, 0), (int(proj["x"]), int(proj["y"])), proj["radius"])

    def update(self):
        self.update_projectiles()
        super().update()

    def draw(self, surface):
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
        self.stealth_cooldown = 5000
        self.last_stealth_time = 0

    def try_stealth(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_stealth_time > self.stealth_cooldown:
            self.is_hidden = True
            self.last_stealth_time = current_time
            return True
        return False

    def ambush_attack(self, player):
        if self.is_hidden:
            self.is_hidden = False
            damage = self.damage * 1.5
            player.health -= damage
            return damage
        return self.attack(player)

    def draw(self, surface):
        if self.is_hidden:
            s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            s.fill((*TYRANID_COLORS.get("lictor", (120,40,120)), 100))
            surface.blit(s, (self.x, self.y))
            self.draw_health_bar(surface)
        else:
            super().draw(surface)

class Carnifex(TyranidSprite):
    """Carnifex - Heavy tank-like creature with devastating attacks"""
    def __init__(self, x, y):
        super().__init__(x, y, 80, 80, "carnifex", 200, 30, 1)
        self.attack_range = 70
        self.attack_cooldown = 2000

    def ground_pound(self, player_x, player_y, player):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        if distance < 100:
            damage = self.damage * (1 - distance/100)
            player.health -= damage
            return damage
        return 0

class Zoanthrope(TyranidSprite):
    """Zoanthrope - Psychic creature with ranged attacks"""
    def __init__(self, x, y):
        super().__init__(x, y, 40, 60, "zoanthrope", 70, 15, 1.5)
        self.attack_range = 200
        self.attack_cooldown = 3000
        self.psychic_blast_cooldown = 8000
        self.last_psychic_blast = 0

    def psychic_blast(self, player_x,player_y, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_psychic_blast > self.psychic_blast_cooldown:
            self.last_psychic_blast = current_time
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < self.attack_range:
                damage = self.damage * 2
                player.health -= damage
                return damage
        return 0

    def draw(self, surface):
        super().draw(surface)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_psychic_blast < 500:
            aura_radius = 30 + (current_time - self.last_psychic_blast)//20
            aura_color = (200,100,255,150)
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
        self.psychic_cooldown = 3000
        self.last_psychic_time = 0

    def update(self):
        super().update()
        self.wings_angle = (self.wings_angle + self.wings_speed) % (2*math.pi)

    def psychic_scream(self, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_psychic_time > self.psychic_cooldown:
            self.last_psychic_time = current_time
            return True
        return False

    def draw(self, surface):
        # draw body
        pygame.draw.rect(surface, TYRANID_COLORS.get("hive_tyrant", (200,0,0)),
                         (self.x, self.y, self.width, self.height))
        # wings
        wing_len = 40
        for side in (-1,1):
            wx = self.x + self.width//2
            wy = self.y + self.height//2
            ex = wx + math.cos(self.wings_angle + side*math.pi/2)*wing_len
            ey = wy + math.sin(self.wings_angle + side*math.pi/2)*wing_len
            pygame.draw.line(surface, (TYRANID_COLORS.get("hive_tyrant")[0]//2,
                                      TYRANID_COLORS.get("hive_tyrant")[1]//2,
                                      TYRANID_COLORS.get("hive_tyrant")[2]//2),
                                      (wx, wy), (ex, ey), 5)
        # psychic bar
        bar_w, bar_h = 60, 5
        px = self.x + (self.width-bar_w)//2
        py = self.y - 15
        pygame.draw.rect(surface, (100,100,100), (px, py, bar_w, bar_h))
        pygame.draw.rect(surface, (200,200,0), (px, py, bar_w*(self.psychic_power/self.max_psychic_power), bar_h))
        self.draw_health_bar(surface)

class Harpy(TyranidSprite):
    """Flying Tyranid with ranged attacks and swooping abilities"""
    def __init__(self, x, y):
        super().__init__(x, y, 60, 60, "harpy", 150, 25, 5)
        self.is_flying = True
        self.swoop_cooldown = 5000
        self.last_swoop_time = 0
        self.swoop_target = None
        self.swoop_speed = 10
        self.wing_angle = 0
        self.wing_speed = 0.2

    def update(self):
        super().update()
        self.wing_angle = (self.wing_angle + self.wing_speed) % (2*math.pi)

    def swoop_attack(self, player_x, player_y):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_swoop_time > self.swoop_cooldown:
            self.last_swoop_time = current_time
            self.swoop_target = (player_x, player_y)
            self.is_flying = False
            return True
        return False

    def draw(self, surface):
        pygame.draw.ellipse(surface, TYRANID_COLORS.get("harpy", (0,150,150)),
                            (self.x, self.y, self.width, self.height))
        wing_len = 50
        for side in (-1,1):
            wx = self.x + self.width//2
            wy = self.y + self.height//2
            ex = wx + math.cos(self.wing_angle + side*math.pi/2)*wing_len
            ey = wy + math.sin(self.wing_angle + side*math.pi/2)*wing_len
            pygame.draw.line(surface,
                              (TYRANID_COLORS.get("harpy")[0]//2,
                               TYRANID_COLORS.get("harpy")[1]//2,
                               TYRANID_COLORS.get("harpy")[2]//2),
                              (wx, wy), (ex, ey), 4)
        self.draw_health_bar(surface)

class Mawloc(TyranidSprite):
    """Burrowing Tyranid that can emerge from the ground"""
    def __init__(self, x, y):
        super().__init__(x, y, 100, 100, "mawloc", 400, 50, 2)
        self.is_burrowed = True
        self.burrow_cooldown = 8000
        self.last_burrow_time = 0
        self.emergence_time = 0
        self.emergence_duration = 1000

    def update(self):
        super().update()
        if not self.is_burrowed:
            current_time = pygame.time.get_ticks()
            if current_time - self.emergence_time > self.emergence_duration:
                self.is_burrowed = True
                self.last_burrow_time = current_time

    def emerge(self, target_x, target_y):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_burrow_time > self.burrow_cooldown:
            self.x, self.y = target_x, target_y
            self.is_burrowed = False
            self.emergence_time = current_time
            return True
        return False

    def draw(self, surface):
        if not self.is_burrowed:
            progress = min(1.0, (pygame.time.get_ticks() - self.emergence_time) / self.emergence_duration)
            height = int(self.height * progress)
            pygame.draw.ellipse(surface, TYRANID_COLORS.get("mawloc", (100,0,100)),
                                (self.x, self.y + self.height - height, self.width, height))
            mandible_len = 30
            for side in (-1,1):
                sx = self.x + self.width//2
                sy = self.y + self.height - height
                ex = sx + side * mandible_len
                ey = sy - 20
                pygame.draw.line(surface,
                                 (TYRANID_COLORS.get("mawloc")[0]//2,
                                  TYRANID_COLORS.get("mawloc")[1]//2,
                                  TYRANID_COLORS.get("mawloc")[2]//2),
                                 (sx, sy), (ex, ey), 5)
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
 #       "hive_tyrant": HiveTyrant,
 #       "harpy": Harpy,
        "mawloc": Mawloc
    }
    klass = tyranid_classes.get(tyranid_type.lower())
    return klass(x, y) if klass else None

# Expose API
__all__ = [
    "TyranidSprite", "Genestealer", "TyranidWarrior", "Gaunt", "Lictor",
    "Carnifex", "Zoanthrope", "HiveTyrant", "Harpy", "Mawloc",
    "create_tyranid"
]
