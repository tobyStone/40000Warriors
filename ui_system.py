import pygame
import os
import math

class UISystem:
    """Class to handle all UI elements in the game"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.SysFont('Arial', 32)
        self.normal_font = pygame.font.SysFont('Arial', 20)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Colors
        self.text_color = (255, 255, 255)
        self.health_color = (0, 255, 0)
        self.health_bg_color = (255, 0, 0)
        self.armor_color = (0, 100, 255)
        self.enemy_health_color = (255, 100, 100)
        self.enemy_health_bg_color = (100, 0, 0)
        
        # UI elements
        self.player_health_bar = HealthBar(20, 20, 200, 20, "HEALTH")
        self.player_armor_bar = HealthBar(20, 50, 200, 15, "ARMOR", self.armor_color)
        self.enemy_health_bar = HealthBar(self.screen_width - 220, 20, 200, 20, "ENEMY", self.enemy_health_color, self.enemy_health_bg_color)
        
        # Fullscreen button
        self.fullscreen_button = Button(
            self.screen_width - 200,
            10,
            180,
            30,
            "Press F for Fullscreen",
            self.toggle_fullscreen
        )
        
        # Game messages
        self.messages = []
        self.message_duration = 3000  # milliseconds
        
        # Dialogue box
        self.dialogue_active = False
        self.current_dialogue = ""
        self.dialogue_speaker = ""
        self.dialogue_timer = 0
        self.dialogue_duration = 5000  # milliseconds
        
        # Minimap
        self.minimap = Minimap(self.screen_width - 120, self.screen_height - 120, 100, 100)
        
        # Ammo counter
        self.ammo_counter = AmmoCounter(20, self.screen_height - 50)
        
        # Kill counter
        self.kill_counter = Counter(self.screen_width - 150, 80, "KILLS", 0)
        
        # Game timer
        self.game_timer = GameTimer(20, 80)
        
        # Objective tracker
        self.objective_tracker = ObjectiveTracker(20, self.screen_height - 100)
        
        # Fullscreen state
        self.is_fullscreen = False
        
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        pygame.display.toggle_fullscreen()

    def handle_events(self, event):
        """Handle UI-related events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.fullscreen_button.is_clicked(event.pos):
                self.fullscreen_button.on_click()

    def update_player_health(self, current_health, max_health):
        """Update the player health bar"""
        self.player_health_bar.update(current_health, max_health)
    
    def update_player_armor(self, current_armor, max_armor):
        """Update the player armor bar"""
        self.player_armor_bar.update(current_armor, max_armor)
    
    def update_enemy_health(self, current_health, max_health):
        """Update the enemy health bar"""
        self.enemy_health_bar.update(current_health, max_health)
    
    def add_message(self, text, color=(255, 255, 255)):
        """Add a temporary message to the screen"""
        self.messages.append({
            "text": text,
            "color": color,
            "time": pygame.time.get_ticks()
        })
    
    def show_dialogue(self, text, speaker=""):
        """Show a dialogue box with text"""
        self.dialogue_active = True
        self.current_dialogue = text
        self.dialogue_speaker = speaker
        self.dialogue_timer = pygame.time.get_ticks()
    
    def update_ammo(self, current_ammo, max_ammo):
        """Update the ammo counter"""
        self.ammo_counter.update(current_ammo, max_ammo)
    
    def increment_kills(self):
        """Increment the kill counter"""
        self.kill_counter.increment()
    
    def set_objective(self, objective_text):
        """Set the current objective"""
        self.objective_tracker.set_objective(objective_text)
    
    def complete_objective(self):
        """Mark the current objective as complete"""
        self.objective_tracker.complete_current_objective()
    
    def update_minimap(self, player_pos, enemies, npcs, exits):
        """Update the minimap with entity positions"""
        self.minimap.update(player_pos, enemies, npcs, exits)
    
    def update(self):
        """Update all UI elements"""
        current_time = pygame.time.get_ticks()
        
        # Update messages (remove expired ones)
        self.messages = [msg for msg in self.messages 
                        if current_time - msg["time"] < self.message_duration]
        
        # Update dialogue
        if self.dialogue_active and current_time - self.dialogue_timer > self.dialogue_duration:
            self.dialogue_active = False
        
        # Update game timer
        self.game_timer.update()
    
    def draw(self, surface):
        """Draw all UI elements"""
        # Draw health bars
        self.player_health_bar.draw(surface)
        self.player_armor_bar.draw(surface)
        self.enemy_health_bar.draw(surface)
        
        # Draw fullscreen button
        self.fullscreen_button.draw(surface)
        
        # Draw messages
        for i, msg in enumerate(self.messages):
            text_surface = self.normal_font.render(msg['text'], True, msg['color'])
            surface.blit(text_surface, (20, self.screen_height - 100 - i * 30))
        
        # Draw dialogue if active
        if self.dialogue_active:
            self.draw_dialogue_box(surface)
        
        # Draw minimap
        self.minimap.draw(surface)
        
        # Draw ammo counter
        self.ammo_counter.draw(surface)
        
        # Draw kill counter
        self.kill_counter.draw(surface)
        
        # Draw game timer
        self.game_timer.draw(surface)
        
        # Draw objective tracker
        self.objective_tracker.draw(surface)
    
    def draw_dialogue_box(self, surface):
        """Draw the dialogue box"""
        # Draw box background
        box_width = self.screen_width - 100
        box_height = 100
        box_x = 50
        box_y = self.screen_height - 150
        
        # Semi-transparent background
        s = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        surface.blit(s, (box_x, box_y))
        
        # Draw border
        pygame.draw.rect(surface, (200, 200, 200), (box_x, box_y, box_width, box_height), 2)
        
        # Draw speaker name if provided
        if self.dialogue_speaker:
            speaker_surface = self.normal_font.render(self.dialogue_speaker, True, (255, 255, 0))
            surface.blit(speaker_surface, (box_x + 10, box_y + 10))
            text_y = box_y + 40
        else:
            text_y = box_y + 20
        
        # Draw dialogue text with word wrapping
        words = self.current_dialogue.split(' ')
        line = ""
        for word in words:
            test_line = line + word + " "
            test_surface = self.normal_font.render(test_line, True, self.text_color)
            if test_surface.get_width() > box_width - 20:
                text_surface = self.normal_font.render(line, True, self.text_color)
                surface.blit(text_surface, (box_x + 10, text_y))
                text_y += 25
                line = word + " "
            else:
                line = test_line
        
        # Draw the last line
        if line:
            text_surface = self.normal_font.render(line, True, self.text_color)
            surface.blit(text_surface, (box_x + 10, text_y))


class HealthBar:
    """Health bar UI element"""
    def __init__(self, x, y, width, height, label="", color=(0, 255, 0), bg_color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.color = color
        self.bg_color = bg_color
        self.current = 100
        self.maximum = 100
        self.font = pygame.font.SysFont('Arial', 16)
    
    def update(self, current, maximum):
        """Update health values"""
        self.current = current
        self.maximum = maximum
    
    def draw(self, surface):
        """Draw the health bar"""
        # Draw background
        pygame.draw.rect(surface, self.bg_color, (self.x, self.y, self.width, self.height))
        
        # Draw health
        health_width = int(self.width * (self.current / self.maximum))
        pygame.draw.rect(surface, self.color, (self.x, self.y, health_width, self.height))
        
        # Draw border
        pygame.draw.rect(surface, (255, 255, 255), (self.x, self.y, self.width, self.height), 1)
        
        # Draw label
        if self.label:
            label_surface = self.font.render(self.label, True, (255, 255, 255))
            surface.blit(label_surface, (self.x, self.y - 20))
        
        # Draw health value
        value_text = f"{int(self.current)}/{int(self.maximum)}"
        value_surface = self.font.render(value_text, True, (255, 255, 255))
        surface.blit(value_surface, (self.x + self.width // 2 - value_surface.get_width() // 2, 
                                    self.y + self.height // 2 - value_surface.get_height() // 2))


class Minimap:
    """Minimap UI element"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.player_pos = (0, 0)
        self.enemies = []
        self.npcs = []
        self.exits = []
        self.scale_factor = 0.1  # Scale from game world to minimap
    
    def update(self, player_pos, enemies, npcs, exits):
        """Update entity positions"""
        self.player_pos = player_pos
        self.enemies = enemies
        self.npcs = npcs
        self.exits = exits
    
    def draw(self, surface):
        """Draw the minimap"""
        # Draw background
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        surface.blit(s, (self.x, self.y))
        
        # Draw border
        pygame.draw.rect(surface, (200, 200, 200), (self.x, self.y, self.width, self.height), 2)
        
        # Draw player (white dot)
        player_x = self.x + int(self.player_pos[0] * self.scale_factor)
        player_y = self.y + int(self.player_pos[1] * self.scale_factor)
        pygame.draw.circle(surface, (255, 255, 255), (player_x, player_y), 3)
        
        # Draw enemies (red dots)
        for enemy in self.enemies:
            enemy_x = self.x + int(enemy[0] * self.scale_factor)
            enemy_y = self.y + int(enemy[1] * self.scale_factor)
            pygame.draw.circle(surface, (255, 0, 0), (enemy_x, enemy_y), 2)
        
        # Draw NPCs (blue dots)
        for npc in self.npcs:
            npc_x = self.x + int(npc[0] * self.scale_factor)
            npc_y = self.y + int(npc[1] * self.scale_factor)
            pygame.draw.circle(surface, (0, 0, 255), (npc_x, npc_y), 2)
        
        # Draw exits (yellow squares)
        for exit in self.exits:
            exit_x = self.x + int(exit[0] * self.scale_factor)
            exit_y = self.y + int(exit[1] * self.scale_factor)
            pygame.draw.rect(surface, (255, 255, 0), (exit_x - 2, exit_y - 2, 4, 4))


class AmmoCounter:
    """Ammo counter UI element"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.current_ammo = 30
        self.max_ammo = 30
        self.font = pygame.font.SysFont('Arial', 24)
    
    def update(self, current_ammo, max_ammo):
        """Update ammo values"""
        self.current_ammo = current_ammo
        self.max_ammo = max_ammo
    
    def draw(self, surface):
        """Draw the ammo counter"""
        # Draw ammo icon (bullet shape)
        pygame.draw.rect(surface, (255, 255, 0), (self.x, self.y + 5, 5, 15))
        pygame.draw.rect(surface, (200, 200, 0), (self.x + 5, self.y, 10, 25))
        
        # Draw ammo text
        ammo_text = f"{self.current_ammo}/{self.max_ammo}"
        text_surface = self.font.render(ammo_text, True, (255, 255, 255))
        surface.blit(text_surface, (self.x + 25, self.y))


class Counter:
    """Generic counter UI element"""
    def __init__(self, x, y, label, initial_value=0):
        self.x = x
        self.y = y
        self.label = label
        self.value = initial_value
        self.font = pygame.font.SysFont('Arial', 20)
    
    def increment(self, amount=1):
        """Increment the counter"""
        self.value += amount
    
    def reset(self):
        """Reset the counter to zero"""
        self.value = 0
    
    def draw(self, surface):
        """Draw the counter"""
        # Draw label
        label_surface = self.font.render(self.label, True, (200, 200, 200))
        surface.blit(label_surface, (self.x, self.y))
        
        # Draw value
        value_surface = self.font.render(str(self.value), True, (255, 255, 255))
        surface.blit(value_surface, (self.x + label_surface.get_width() + 10, self.y))


class GameTimer:
    """Game timer UI element"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.font = pygame.font.SysFont('Arial', 20)
    
    def update(self):
        """Update the timer"""
        # Timer updates automatically based on current time
        pass
    
    def reset(self):
        """Reset the timer"""
        self.start_time = pygame.time.get_ticks()
    
    def get_time_string(self):
        """Get the formatted time string"""
        elapsed = pygame.time.get_ticks() - self.start_time
        seconds = elapsed // 1000
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def draw(self, surface):
        """Draw the timer"""
        time_string = self.get_time_string()
        text_surface = self.font.render(time_string, True, (255, 255, 255))
        surface.blit(text_surface, (self.x, self.y))


class ObjectiveTracker:
    """Objective tracker UI element"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.objectives = []
        self.current_objective = ""
        self.font = pygame.font.SysFont('Arial', 18)
        self.title_font = pygame.font.SysFont('Arial', 22)
    
    def set_objective(self, objective_text):
        """Set the current objective"""
        self.current_objective = objective_text
        self.objectives.append({
            "text": objective_text,
            "completed": False
        })
    
    def complete_current_objective(self):
        """Mark the current objective as complete"""
        for obj in self.objectives:
            if obj["text"] == self.current_objective:
                obj["completed"] = True
                break
    
    def draw(self, surface):
        """Draw the objective tracker"""
        # Draw title
        title_surface = self.title_font.render("OBJECTIVES", True, (255, 200, 0))
        surface.blit(title_surface, (self.x, self.y))
        
        # Draw objectives
        y_offset = self.y + 30
        for obj in self.objectives:
            # Draw bullet point
            if obj["completed"]:
                pygame.draw.rect(surface, (0, 255, 0), (self.x, y_offset + 8, 10, 10))
            else:
                pygame.draw.rect(surface, (255, 255, 0), (self.x, y_offset + 8, 10, 10))
            
            # Draw text
            color = (150, 150, 150) if obj["completed"] else (255, 255, 255)
            text_surface = self.font.render(obj["text"], True, color)
            surface.blit(text_surface, (self.x + 20, y_offset))
            
            y_offset += 25


class Button:
    def __init__(self, x, y, width, height, text, on_click):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.on_click = on_click
        self.font = pygame.font.SysFont('Arial', 16)
        self.is_hovered = False
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def draw(self, surface):
        # Draw button background
        color = (100, 100, 100) if self.is_hovered else (50, 50, 50)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        
        # Draw button text
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
