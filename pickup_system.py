import pygame
import random
import math
import os

class Pickup:
    """Base class for all pickups"""
    def __init__(self, x, y, width, height, pickup_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.pickup_type = pickup_type
        self.active = True
        self.collected = False
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 30000  # 30 seconds
        self.pulse_speed = 0.05
        self.pulse_phase = 0
        self.rotation = 0
        self.rotation_speed = 1
        
        # Visual properties
        self.color = self.get_color_for_type()
        self.glow_color = self.get_glow_color()
        self.glow_radius = 20
        self.glow_intensity = 0.5
    
    def get_color_for_type(self):
        """Get base color based on pickup type"""
        colors = {
            "ammo": (255, 200, 0),      # Gold
            "health": (0, 255, 0),      # Green
            "armor": (0, 100, 255),     # Blue
            "powerup": (255, 0, 255),   # Purple
            "key": (255, 255, 255)      # White
        }
        return colors.get(self.pickup_type, (255, 255, 255))
    
    def get_glow_color(self):
        """Get glow color based on pickup type"""
        base_color = self.get_color_for_type()
        return (base_color[0], base_color[1], base_color[2], 128)
    
    def update(self):
        """Update pickup state"""
        current_time = pygame.time.get_ticks()
        
        # Check lifetime
        if current_time - self.spawn_time > self.lifetime:
            self.active = False
            return
        
        # Update animation
        self.pulse_phase += self.pulse_speed
        if self.pulse_phase > 2 * math.pi:
            self.pulse_phase = 0
        
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation = 0
    
    def draw(self, surface):
        """Draw the pickup"""
        if not self.active:
            return
        
        # Draw glow
        pulse_radius = self.glow_radius + math.sin(self.pulse_phase) * 5
        glow_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, self.glow_color,
                         (pulse_radius, pulse_radius), pulse_radius)
        surface.blit(glow_surface,
                    (self.x + self.width//2 - pulse_radius,
                     self.y + self.height//2 - pulse_radius))
        
        # Draw pickup
        pickup_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_pickup_shape(pickup_surface)
        
        # Rotate and draw
        rotated_surface = pygame.transform.rotate(pickup_surface, self.rotation)
        surface.blit(rotated_surface,
                    (self.x + self.width//2 - rotated_surface.get_width()//2,
                     self.y + self.height//2 - rotated_surface.get_height()//2))
    
    def draw_pickup_shape(self, surface):
        """Draw the specific shape for this pickup type"""
        if self.pickup_type == "ammo":
            # Draw ammo crate
            pygame.draw.rect(surface, self.color, (0, 0, self.width, self.height))
            pygame.draw.rect(surface, (100, 100, 100), (0, 0, self.width, self.height), 2)
            # Draw ammo symbol
            pygame.draw.rect(surface, (200, 200, 200),
                           (self.width//4, self.height//4,
                            self.width//2, self.height//2))
        elif self.pickup_type == "health":
            # Draw health pack
            pygame.draw.rect(surface, self.color, (0, 0, self.width, self.height))
            pygame.draw.rect(surface, (100, 100, 100), (0, 0, self.width, self.height), 2)
            # Draw cross
            cross_width = self.width//3
            pygame.draw.rect(surface, (255, 255, 255),
                           (self.width//2 - cross_width//2, self.height//4,
                            cross_width, self.height//2))
            pygame.draw.rect(surface, (255, 255, 255),
                           (self.width//4, self.height//2 - cross_width//2,
                            self.width//2, cross_width))
        elif self.pickup_type == "armor":
            # Draw armor pickup
            pygame.draw.rect(surface, self.color, (0, 0, self.width, self.height))
            pygame.draw.rect(surface, (100, 100, 100), (0, 0, self.width, self.height), 2)
            # Draw shield symbol
            pygame.draw.arc(surface, (255, 255, 255),
                          (self.width//4, self.height//4,
                           self.width//2, self.height//2),
                          0, math.pi, 2)
        else:
            # Default shape
            pygame.draw.rect(surface, self.color, (0, 0, self.width, self.height))
            pygame.draw.rect(surface, (100, 100, 100), (0, 0, self.width, self.height), 2)
    
    def collect(self, player):
        """Handle pickup collection"""
        if not self.active or self.collected:
            return False
        
        self.collected = True
        self.active = False
        return True

    def load_pickup_sprite(self, sprite_name):
        """Load a sprite for the pickup"""
        try:
            # Get the project root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            
            # Construct the path to the sprite
            path = os.path.join(project_root, "40000Warriors", "assets", sprite_name)
            
            # Load and return the sprite
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load pickup sprite: {sprite_name}")
            print(f"Error: {e}")
            print(f"Attempted path: {path}")
            # Return a colored placeholder surface
            surface = pygame.Surface((32, 32), pygame.SRCALPHA)
            surface.fill((255, 215, 0))  # Gold for missing pickup textures
            pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)  # Black border
            return surface

class AmmoCrate(Pickup):
    """Specialized ammo pickup"""
    def __init__(self, x, y, ammo_type=None, ammo_amount=None):
        super().__init__(x, y, 40, 40, "ammo")
        
        # If no specific type/amount provided, randomize them
        if ammo_type is None:
            self.ammo_types = ["bolter", "plasma", "melta"]
            self.ammo_type = random.choice(self.ammo_types)
        else:
            self.ammo_type = ammo_type
            
        if ammo_amount is None:
            self.ammo_amount = random.randint(50, 100)
        else:
            self.ammo_amount = ammo_amount
        
        # Update color based on ammo type
        ammo_colors = {
            "bolter": (255, 200, 0),  # Gold
            "plasma": (0, 200, 255),  # Cyan
            "melta": (255, 100, 0)    # Orange
        }
        self.color = ammo_colors.get(self.ammo_type, (255, 200, 0))
        self.glow_color = (*self.color, 128)
        
    def collect(self, player):
        """Add ammo to the player's inventory based on ammo type"""
        if not self.collected:
            ammo_added = 0
            if self.ammo_type == "bolter":
                space_left = player.max_bolter_ammo - player.bolter_ammo
                ammo_added = min(space_left, self.ammo_amount)
                player.bolter_ammo += ammo_added
            elif self.ammo_type == "plasma":
                space_left = player.max_plasma_ammo - player.plasma_ammo
                ammo_added = min(space_left, self.ammo_amount)
                player.plasma_ammo += ammo_added
            elif self.ammo_type == "melta":
                space_left = player.max_melta_ammo - player.melta_ammo
                ammo_added = min(space_left, self.ammo_amount)
                player.melta_ammo += ammo_added
                
            self.collected = True
            return ammo_added > 0  # Return True if any ammo was actually added
        return False
    
    def draw_pickup_shape(self, surface):
        """Draw ammo crate specific shape"""
        # Draw crate
        pygame.draw.rect(surface, self.color, (0, 0, self.width, self.height))
        pygame.draw.rect(surface, (100, 100, 100), (0, 0, self.width, self.height), 2)
        
        # Draw ammo type symbol
        if self.ammo_type == "bolter":
            # Draw bolter rounds
            for i in range(3):
                pygame.draw.rect(surface, (200, 200, 200),
                               (self.width//4, self.height//4 + i*8,
                                self.width//2, 4))
        elif self.ammo_type == "plasma":
            # Draw plasma cells
            pygame.draw.ellipse(surface, (200, 200, 200),
                              (self.width//4, self.height//4,
                               self.width//2, self.height//2))
        elif self.ammo_type == "melta":
            # Draw melta fuel
            pygame.draw.rect(surface, (200, 200, 200),
                           (self.width//4, self.height//4,
                            self.width//2, self.height//2))

class PickupManager:
    """Manager for handling pickups in the game"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pickups = []
        self.spawn_timer = 0
        self.spawn_interval = 30000  # 30 seconds
        self.max_pickups = 5
    
    def update(self):
        """Update all pickups"""
        current_time = pygame.time.get_ticks()
        
        # Spawn new pickups
        if current_time - self.spawn_timer > self.spawn_interval and len(self.pickups) < self.max_pickups:
            self.spawn_random_pickup()
            self.spawn_timer = current_time
        
        # Update existing pickups
        for pickup in self.pickups[:]:
            pickup.update()
            if not pickup.active:
                self.pickups.remove(pickup)
    
    def draw(self, surface):
        """Draw all pickups"""
        for pickup in self.pickups:
            pickup.draw(surface)
    
    def spawn_random_pickup(self):
        """Spawn a random pickup at a valid location"""
        x = random.randint(50, self.screen_width - 50)
        y = random.randint(50, self.screen_height - 50)
        
        # Create ammo crate (for now, we can add other types later)
        pickup = AmmoCrate(x, y)
        self.pickups.append(pickup)
    
    def check_collisions(self, player):
        """Check for collisions between player and pickups"""
        for pickup in self.pickups:
            if (abs(player.x - pickup.x) < (player.width + pickup.width)//2 and
                abs(player.y - pickup.y) < (player.height + pickup.height)//2):
                if pickup.collect(player):
                    self.pickups.remove(pickup)
                    return True
        return False

def create_pickup(pickup_type, x, y):
    """Factory function to create pickups"""
    pickup_classes = {
        "ammo": AmmoCrate
    }
    
    pickup_class = pickup_classes.get(pickup_type.lower())
    if pickup_class:
        return pickup_class(x, y)
    return None 