import pygame
import os
import math
import random

class RoomTransition:
    """Class for room transitions and entrances to new areas"""
    def __init__(self, x, y, width, height, target_room, transition_type="door"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.target_room = target_room
        self.transition_type = transition_type  # door, portal, elevator, stairs
        self.color = self.get_color_for_type()
        self.sprite = None
        self.is_locked = False
        self.key_required = None
        self.is_active = True
        self.activation_cooldown = 1000  # milliseconds
        self.last_activation_time = 0
        
        # Visual effects
        self.glow_effect = False
        self.glow_color = (255, 255, 100, 150)  # Yellow with transparency
        self.glow_radius = 30
        self.glow_pulse = 0
        self.glow_direction = 1
        
        # Animation
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.last_animation_update = 0
        self.animation_cooldown = 200  # ms
    
    def get_color_for_type(self):
        """Get color based on transition type"""
        colors = {
            "door": (200, 200, 0),      # Yellow for doors
            "portal": (0, 200, 200),    # Cyan for portals
            "elevator": (200, 100, 0),  # Orange for elevators
            "stairs": (150, 150, 150)   # Gray for stairs
        }
        return colors.get(self.transition_type.lower(), (200, 200, 0))
    
    def load_sprite(self, filename):
        """Load the sprite image from the assets folder"""
        try:
            # Assume assets are located at .../40000Warriors/assets/
            project_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "40000Warriors")
            assets_path = os.path.join(project_root, "assets")
            path = os.path.join(assets_path, filename)
            self.sprite = pygame.image.load(path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
        except pygame.error:
            print(f"Unable to load transition sprite: {filename}")
            # Create a placeholder sprite
            self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.sprite.fill(self.color)
    
    def lock(self, key_name=None):
        """Lock the transition, optionally requiring a specific key"""
        self.is_locked = True
        self.key_required = key_name
    
    def unlock(self, key_name=None):
        """Unlock the transition if the correct key is provided"""
        if not self.is_locked:
            return True
        if self.key_required is None or self.key_required == key_name:
            self.is_locked = False
            return True
        return False
    
    def is_player_colliding(self, player_x, player_y, player_width, player_height):
        """Check if player is colliding with the transition area"""
        return (player_x < self.x + self.width and
                player_x + player_width > self.x and
                player_y < self.y + self.height and
                player_y + player_height > self.y)
    
    def can_activate(self, player_x, player_y, player_width, player_height):
        """Determine if the transition can be activated"""
        if not self.is_active or self.is_locked:
            return False
        current_time = pygame.time.get_ticks()
        cooldown_passed = current_time - self.last_activation_time > self.activation_cooldown
        return self.is_player_colliding(player_x, player_y, player_width, player_height) and cooldown_passed
    
    def activate(self):
        """Activate the transition and return the target room"""
        if self.is_locked:
            return False
        self.last_activation_time = pygame.time.get_ticks()
        return self.target_room
    
    def update_animation(self):
        """Update animation frames and glow pulse effect"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_animation_update > self.animation_cooldown:
            self.last_animation_update = current_time
            self.animation_frame = (self.animation_frame + 1) % 4  # Assuming 4 frames for animation
            self.glow_pulse += 0.1 * self.glow_direction
            if self.glow_pulse > 1:
                self.glow_pulse = 1
                self.glow_direction = -1
            elif self.glow_pulse < 0:
                self.glow_pulse = 0
                self.glow_direction = 1
    
    def update(self):
        """Update the transition's state (animations, etc.)"""
        self.update_animation()
    
    def draw(self, surface):
        """Draw the transition with visual effects and sprite/placeholder"""
        # Draw glow effect if enabled
        if self.glow_effect:
            glow_size = self.glow_radius * 2
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            alpha = int(100 + 155 * self.glow_pulse)
            color = (self.glow_color[0], self.glow_color[1], self.glow_color[2], alpha)
            for radius in range(self.glow_radius, 0, -1):
                alpha_factor = radius / self.glow_radius
                current_alpha = int(alpha * alpha_factor)
                current_color = (color[0], color[1], color[2], current_alpha)
                pygame.draw.circle(glow_surf, current_color, (self.glow_radius, self.glow_radius), radius)
            glow_x = self.x + self.width // 2 - self.glow_radius
            glow_y = self.y + self.height // 2 - self.glow_radius
            surface.blit(glow_surf, (glow_x, glow_y))
        
        # Draw the sprite if available, otherwise draw a rectangle
        if self.sprite:
            surface.blit(self.sprite, (self.x, self.y))
        else:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw lock indicator if locked
        if self.is_locked:
            lock_color = (255, 0, 0)
            lock_x = self.x + self.width // 2 - 5
            lock_y = self.y - 15
            pygame.draw.rect(surface, lock_color, (lock_x, lock_y, 10, 10))
            pygame.draw.rect(surface, lock_color, (lock_x + 2, lock_y - 5, 6, 5))


class RoomManager:
    """Class to manage multiple rooms and transitions between them"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.rooms = {}
        self.current_room_id = None
        self.transition_effect = None
        self.transition_progress = 0
        self.transition_speed = 0.05
        self.is_transitioning = False
        self.next_room_id = None
        
        # Pre-generate transition effect surfaces for effects like fade, wipe, and portal
        self.transition_surfaces = {}
        self.generate_transition_effects()
    
    def generate_transition_effects(self):
        """Generate surfaces for different transition effects"""
        fade_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        fade_surf.fill((0, 0, 0, 0))  # Start fully transparent
        self.transition_surfaces["fade"] = fade_surf
        
        wipe_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        wipe_surf.fill((0, 0, 0, 255))
        self.transition_surfaces["wipe"] = wipe_surf
        
        portal_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for i in range(10):
            radius = i * 30
            alpha = 255 - (i * 25)
            pygame.draw.circle(portal_surf, (0, 200, 200, alpha),
                               (self.screen_width // 2, self.screen_height // 2), radius, 5)
        self.transition_surfaces["portal"] = portal_surf
    
    def add_room(self, room_id, room):
        """Add a room to the manager and set it as the current room if none exists"""
        self.rooms[room_id] = room
        if self.current_room_id is None:
            self.current_room_id = room_id
    
    def get_current_room(self):
        """Retrieve the current active room"""
        return self.rooms.get(self.current_room_id)
    
    def transition_to_room(self, room_id, effect="fade"):
        """Begin a transition to a new room using a specified effect"""
        if room_id not in self.rooms or self.is_transitioning:
            return False
        self.is_transitioning = True
        self.next_room_id = room_id
        self.transition_effect = effect
        self.transition_progress = 0
        return True
    
    def update_transition(self):
        """Update the state of the room transition effect"""
        if not self.is_transitioning:
            return
        self.transition_progress += self.transition_speed
        if self.transition_progress >= 1:
            self.current_room_id = self.next_room_id
            self.next_room_id = None
            self.is_transitioning = False
            self.transition_progress = 0
    
    def update(self):
        """Update the room manager and current room state"""
        self.update_transition()
        current_room = self.get_current_room()
        if current_room:
            current_room.update()
    
    def draw(self, surface):
        """Draw the current room and any active transition effects"""
        current_room = self.get_current_room()
        if current_room:
            current_room.draw(surface)
        
        if self.is_transitioning:
            if self.transition_effect == "fade":
                alpha = int(255 * self.transition_progress) if self.transition_progress < 0.5 else int(255 * (1 - self.transition_progress) * 2)
                fade_surf = self.transition_surfaces["fade"].copy()
                fade_surf.fill((0, 0, 0, alpha))
                surface.blit(fade_surf, (0, 0))
            elif self.transition_effect == "wipe":
                wipe_width = int(self.screen_width * self.transition_progress)
                surface.blit(self.transition_surfaces["wipe"], (0, 0), (0, 0, wipe_width, self.screen_height))
            elif self.transition_effect == "portal":
                portal_surf = self.transition_surfaces["portal"].copy()
                if self.transition_progress < 0.5:
                    scale = self.transition_progress * 2
                else:
                    scale = (1 - self.transition_progress) * 2
                scaled_size = (int(self.screen_width * scale), int(self.screen_height * scale))
                if scaled_size[0] > 0 and scaled_size[1] > 0:
                    scaled_portal = pygame.transform.scale(portal_surf, scaled_size)
                    x = (self.screen_width - scaled_portal.get_width()) // 2
                    y = (self.screen_height - scaled_portal.get_height()) // 2
                    surface.blit(scaled_portal, (x, y))


class Room:
    """Class representing a game room with background, entities, and transitions"""
    def __init__(self, room_id, background_image=None):
        self.room_id = room_id
        self.background = background_image
        self.interior_3d = None  # Optional 3D interior effect
        self.enemies = []
        self.npcs = []
        self.transitions = []
        self.items = []
        self.graffiti = []
        self.decorations = []
        self.light_sources = []
        
        # Additional room properties
        self.ambient_light = 0.7
        self.fog_enabled = False
        self.fog_color = (200, 200, 220, 30)
        self.fog_density = 0.3
        
        # Room state flags
        self.is_cleared = False
        self.is_visited = False
        self.special_events = []
    
    def set_interior_3d(self, interior_3d):
        """Set a 3D interior effect for the room"""
        self.interior_3d = interior_3d
    
    def add_enemy(self, enemy):
        self.enemies.append(enemy)
    
    def add_npc(self, npc):
        self.npcs.append(npc)
    
    def add_transition(self, transition):
        self.transitions.append(transition)
    
    def add_item(self, item):
        self.items.append(item)
    
    def add_graffiti(self, x, y, text, color=(255, 0, 0)):
        self.graffiti.append({"x": x, "y": y, "text": text, "color": color})
    
    def add_decoration(self, x, y, width, height, image=None, color=(100, 100, 100)):
        self.decorations.append({
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "image": image,
            "color": color
        })
    
    def add_light_source(self, x, y, color=(255, 200, 100), radius=100, intensity=0.8):
        self.light_sources.append({
            "x": x,
            "y": y,
            "color": color,
            "radius": radius,
            "intensity": intensity,
            "flicker": random.uniform(0.9, 1.1)
        })
    
    def add_special_event(self, event_type, trigger_condition, event_data):
        self.special_events.append({
            "type": event_type,
            "trigger": trigger_condition,
            "data": event_data,
            "triggered": False
        })
    
    def check_special_events(self, player):
        for event in self.special_events:
            if not event["triggered"] and event["trigger"](player, self):
                event["triggered"] = True
                return event
        return None
    
    def update(self):
        """Update the state of the room, its entities, and transitions"""
        if self.interior_3d:
            self.interior_3d.update()
        for transition in self.transitions:
            transition.update()
        for npc in self.npcs:
            npc.update()
        for enemy in self.enemies:
            enemy.update()
        if not self.is_cleared and len(self.enemies) == 0:
            self.is_cleared = True
    
    def draw(self, surface):
        """Draw the room, its contents, and transitions"""
        # Draw background or 3D interior if available
        if self.interior_3d:
            self.interior_3d.draw(surface)
        elif self.background:
            scaled_bg = pygame.transform.scale(self.background, (surface.get_width(), surface.get_height()))
            surface.blit(scaled_bg, (0, 0))
        else:
            surface.fill((50, 50, 50))
        
        # Draw decorations
        for decor in self.decorations:
            if decor["image"]:
                surface.blit(decor["image"], (decor["x"], decor["y"]))
            else:
                pygame.draw.rect(surface, decor["color"],
                                 (decor["x"], decor["y"], decor["width"], decor["height"]))
        
        # Draw items
        for item in self.items:
            item.draw(surface)
        
        # Draw NPCs
        for npc in self.npcs:
            npc.draw(surface)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(surface)
        
        # Draw transitions
        for transition in self.transitions:
            transition.draw(surface)

def create_transition(transition_type, x, y, width, height, target_room):
    """Factory function to create a RoomTransition object"""
    return RoomTransition(x, y, width, height, target_room, transition_type)

# Explicitly expose the API for importers
__all__ = ['Room', 'RoomManager', 'RoomTransition', 'create_transition']
