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
        """Load the sprite image"""
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", filename)
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
        """Check if the transition can be activated"""
        if not self.is_active or self.is_locked:
            return False
        
        current_time = pygame.time.get_ticks()
        cooldown_passed = current_time - self.last_activation_time > self.activation_cooldown
        
        return self.is_player_colliding(player_x, player_y, player_width, player_height) and cooldown_passed
    
    def activate(self):
        """Activate the transition"""
        if self.is_locked:
            return False
        
        self.last_activation_time = pygame.time.get_ticks()
        return self.target_room
    
    def update_animation(self):
        """Update animation frames"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_animation_update > self.animation_cooldown:
            self.last_animation_update = current_time
            self.animation_frame = (self.animation_frame + 1) % 4  # Assuming 4 frames
            
            # Update glow pulse effect
            self.glow_pulse += 0.1 * self.glow_direction
            if self.glow_pulse > 1:
                self.glow_pulse = 1
                self.glow_direction = -1
            elif self.glow_pulse < 0:
                self.glow_pulse = 0
                self.glow_direction = 1
    
    def update(self):
        """Update transition state"""
        self.update_animation()
    
    def draw(self, surface):
        """Draw the transition"""
        # Draw glow effect if enabled
        if self.glow_effect:
            # Create a surface for the glow
            glow_size = self.glow_radius * 2
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            
            # Adjust alpha based on pulse
            alpha = int(100 + 155 * self.glow_pulse)
            color = (self.glow_color[0], self.glow_color[1], self.glow_color[2], alpha)
            
            # Draw radial gradient
            for radius in range(self.glow_radius, 0, -1):
                alpha_factor = radius / self.glow_radius
                current_alpha = int(alpha * alpha_factor)
                current_color = (color[0], color[1], color[2], current_alpha)
                pygame.draw.circle(glow_surf, current_color, (self.glow_radius, self.glow_radius), radius)
            
            # Position the glow behind the transition
            glow_x = self.x + self.width//2 - self.glow_radius
            glow_y = self.y + self.height//2 - self.glow_radius
            surface.blit(glow_surf, (glow_x, glow_y))
        
        # Draw the transition
        if self.sprite:
            surface.blit(self.sprite, (self.x, self.y))
        else:
            # Draw placeholder rectangle
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw lock indicator if locked
        if self.is_locked:
            lock_color = (255, 0, 0)  # Red for locked
            lock_x = self.x + self.width//2 - 5
            lock_y = self.y - 15
            
            # Draw lock symbol
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
        
        # Transition effects
        self.transition_surfaces = {}
        self.generate_transition_effects()
    
    def generate_transition_effects(self):
        """Generate transition effect surfaces"""
        # Fade effect
        fade_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        fade_surf.fill((0, 0, 0, 0))  # Start transparent
        self.transition_surfaces["fade"] = fade_surf
        
        # Wipe effect
        wipe_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        wipe_surf.fill((0, 0, 0, 255))  # Solid black
        self.transition_surfaces["wipe"] = wipe_surf
        
        # Portal effect
        portal_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        for i in range(10):
            radius = i * 30
            alpha = 255 - (i * 25)
            pygame.draw.circle(portal_surf, (0, 200, 200, alpha), 
                              (self.screen_width//2, self.screen_height//2), radius, 5)
        self.transition_surfaces["portal"] = portal_surf
    
    def add_room(self, room_id, room):
        """Add a room to the manager"""
        self.rooms[room_id] = room
        if self.current_room_id is None:
            self.current_room_id = room_id
    
    def get_current_room(self):
        """Get the current room"""
        return self.rooms.get(self.current_room_id)
    
    def transition_to_room(self, room_id, effect="fade"):
        """Start a transition to another room"""
        if room_id not in self.rooms or self.is_transitioning:
            return False
        
        self.is_transitioning = True
        self.next_room_id = room_id
        self.transition_effect = effect
        self.transition_progress = 0
        return True
    
    def update_transition(self):
        """Update the room transition effect"""
        if not self.is_transitioning:
            return
        
        self.transition_progress += self.transition_speed
        
        if self.transition_progress >= 1:
            # Transition complete
            self.current_room_id = self.next_room_id
            self.next_room_id = None
            self.is_transitioning = False
            self.transition_progress = 0
    
    def update(self):
        """Update room manager state"""
        self.update_transition()
        
        # Update current room
        current_room = self.get_current_room()
        if current_room:
            current_room.update()
    
    def draw(self, surface):
        """Draw the current room and transition effects"""
        # Draw current room
        current_room = self.get_current_room()
        if current_room:
            current_room.draw(surface)
        
        # Draw transition effect if transitioning
        if self.is_transitioning:
            if self.transition_effect == "fade":
                # Fade to black and back
                alpha = int(255 * self.transition_progress) if self.transition_progress < 0.5 else int(255 * (1 - self.transition_progress) * 2)
                fade_surf = self.transition_surfaces["fade"].copy()
                fade_surf.fill((0, 0, 0, alpha))
                surface.blit(fade_surf, (0, 0))
            
            elif self.transition_effect == "wipe":
                # Wipe across the screen
                wipe_width = int(self.screen_width * self.transition_progress)
                surface.blit(self.transition_surfaces["wipe"], (0, 0), 
                            (0, 0, wipe_width, self.screen_height))
            
            elif self.transition_effect == "portal":
                # Portal effect (grow/shrink circle)
                portal_surf = self.transition_surfaces["portal"].copy()
                if self.transition_progress < 0.5:
                    # Grow the portal
                    scale = self.transition_progress * 2
                else:
                    # Shrink the portal
                    scale = (1 - self.transition_progress) * 2
                
                scaled_size = (int(self.screen_width * scale), int(self.screen_height * scale))
                if scaled_size[0] > 0 and scaled_size[1] > 0:
                    scaled_portal = pygame.transform.scale(portal_surf, scaled_size)
                    surface.blit(scaled_portal, 
                                (self.screen_width//2 - scaled_size[0]//2, 
                                 self.screen_height//2 - scaled_size[1]//2))


class Room:
    """Class representing a game room with background, entities, and transitions"""
    def __init__(self, room_id, background_image=None):
        self.room_id = room_id
        self.background = background_image
        self.interior_3d = None  # For 3D interior effect
        self.enemies = []
        self.npcs = []
        self.transitions = []
        self.items = []
        self.graffiti = []
        self.decorations = []
        self.light_sources = []
        
        # Room properties
        self.ambient_light = 0.7  # Base light level (0-1)
        self.fog_enabled = False
        self.fog_color = (200, 200, 220, 30)
        self.fog_density = 0.3
        
        # Room state
        self.is_cleared = False  # Set to true when all enemies are defeated
        self.is_visited = False  # Set to true when player first enters
        self.special_events = []  # List of special events that can trigger in this room
    
    def set_interior_3d(self, interior_3d):
        """Set the 3D interior effect for this room"""
        self.interior_3d = interior_3d
    
    def add_enemy(self, enemy):
        """Add an enemy to the room"""
        self.enemies.append(enemy)
    
    def add_npc(self, npc):
        """Add an NPC to the room"""
        self.npcs.append(npc)
    
    def add_transition(self, transition):
        """Add a room transition to the room"""
        self.transitions.append(transition)
    
    def add_item(self, item):
        """Add an item to the room"""
        self.items.append(item)
    
    def add_graffiti(self, x, y, text, color=(255, 0, 0)):
        """Add graffiti to the room"""
        self.graffiti.append({"x": x, "y": y, "text": text, "color": color})
    
    def add_decoration(self, x, y, width, height, image=None, color=(100, 100, 100)):
        """Add a decoration to the room"""
        self.decorations.append({
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "image": image,
            "color": color
        })
    
    def add_light_source(self, x, y, color=(255, 200, 100), radius=100, intensity=0.8):
        """Add a light source to the room"""
        self.light_sources.append({
            "x": x,
            "y": y,
            "color": color,
            "radius": radius,
            "intensity": intensity,
            "flicker": random.uniform(0.9, 1.1)  # Individual flicker factor
        })
    
    def add_special_event(self, event_type, trigger_condition, event_data):
        """Add a special event to the room"""
        self.special_events.append({
            "type": event_type,  # spawn, dialogue, effect, etc.
            "trigger": trigger_condition,  # function that returns True when event should trigger
            "data": event_data,  # data needed for the event
            "triggered": False  # whether the event has been triggered
        })
    
    def check_special_events(self, player):
        """Check and trigger special events"""
        for event in self.special_events:
            if not event["triggered"] and event["trigger"](player, self):
                event["triggered"] = True
                return event
        return None
    
    def update(self):
        """Update room state"""
        # Update 3D interior if available
        if self.interior_3d:
            self.interior_3d.update()
        
        # Update transitions
        for transition in self.transitions:
            transition.update()
        
        # Update NPCs
        for npc in self.npcs:
            npc.update()
        
        # Update enemies
        for enemy in self.enemies:
            enemy.update()
        
        # Check if room is cleared (no enemies left)
        if not self.is_cleared and len(self.enemies) == 0:
            self.is_cleared = True
    
    def draw_background(self, surface):
        """Draw the room background"""
        if self.interior_3d:
            # Draw 3D interior
            self.interior_3d.draw(surface)
        elif self.background:
            # Scale background to fit screen
            scaled_bg = pygame.transform.scale(self.background, (surface.get_width(), surface.get_height()))
            surface.blit(scaled_bg, (0, 0))
        else:
            # Default background if none provided
            surface.fill((50, 50, 50))
    
    def draw_graffiti(self, surface):
        """Draw room graffiti"""
        font = pygame.font.SysFont('Arial', 20)
        for g in self.graffiti:
            text_surface = font.render(g["text"], True, g["color"])
            surface.blit(text_surface, (g["x"], g["y"]))
    
    def draw_decorations(self, surface):
        """Dra
(Content truncated due to size limit. Use line ranges to read in chunks)