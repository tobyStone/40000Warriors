import pygame
import os
import math
import random

class NPC:
    """Class for non-player characters that can interact with the player"""
    def __init__(self, x, y, npc_type, name, dialogue_lines=None):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 70
        self.npc_type = npc_type
        self.name = name
        
        # Appearance
        self.color = self.get_color_for_type()
        self.sprite = None
        self.direction = "right"
        
        # Dialogue
        self.dialogue_lines = dialogue_lines or self.get_default_dialogue()
        self.current_dialogue_index = 0
        self.interaction_range = 80
        self.interaction_cooldown = 1000  # milliseconds
        self.last_interaction_time = 0
        
        # Movement
        self.is_moving = False
        self.movement_pattern = "stationary"  # stationary, patrol, follow
        self.patrol_points = []
        self.current_patrol_point = 0
        self.movement_speed = 1
        self.follow_distance = 100
        
        # State
        self.state = "idle"  # idle, talking, moving
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.last_animation_update = 0
        self.animation_cooldown = 200  # ms
        
        # Quest/interaction flags
        self.has_quest = False
        self.quest_given = False
        self.quest_completed = False
        self.quest_text = ""
        self.quest_reward = None
        
        # Items
        self.items = []
    
    def get_color_for_type(self):
        """Get color based on NPC type"""
        colors = {
            "soldier": (0, 100, 200),      # Blue for Imperial Guard
            "tech_priest": (200, 100, 0),  # Orange for Tech Priest
            "inquisitor": (150, 0, 150),   # Purple for Inquisitor
            "commissar": (200, 0, 0),      # Red for Commissar
            "civilian": (0, 150, 0),       # Green for Civilian
            "servitor": (100, 100, 100)    # Gray for Servitor
        }
        return colors.get(self.npc_type.lower(), (200, 200, 200))
    
    def get_default_dialogue(self):
        """Get default dialogue based on NPC type"""
        dialogues = {
            "soldier": [
                "Greetings, Scout. The Emperor protects.",
                "Beware of the Tyranid infestation ahead.",
                "Purge the xenos with extreme prejudice.",
                "We've lost contact with Squad Epsilon in the eastern chambers."
            ],
            "tech_priest": [
                "The Omnissiah guides us.",
                "Your weapons have been blessed by the Machine God.",
                "The alien technology must be studied and destroyed.",
                "I can upgrade your equipment if you bring me the necessary components."
            ],
            "inquisitor": [
                "Trust no one, not even yourself.",
                "The xenos taint must be cleansed with fire.",
                "I sense warp disturbances in this area.",
                "Report any heretical activities directly to me."
            ],
            "commissar": [
                "Failure is not an option, Scout.",
                "Show no fear in the face of the alien.",
                "The Emperor demands victory at any cost.",
                "Retreat is punishable by death."
            ],
            "civilian": [
                "Please help us! The creatures came so suddenly.",
                "I saw them take people away... alive.",
                "Is there any safe way out of here?",
                "Thank the Emperor you've come!"
            ],
            "servitor": [
                "Awaiting instructions.",
                "Systems functioning within acceptable parameters.",
                "Maintenance protocols active.",
                "Biological components stable."
            ]
        }
        return dialogues.get(self.npc_type.lower(), ["Hello.", "I have nothing more to say."])
    
    def load_sprite(self, filename):
        """Load the sprite image"""
        try:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", filename)
            self.sprite = pygame.image.load(path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
        except pygame.error:
            print(f"Unable to load NPC sprite: {filename}")
            # Create a placeholder sprite
            self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.sprite.fill(self.color)
    
    def set_patrol_points(self, points):
        """Set patrol points for the NPC to move between"""
        self.patrol_points = points
        self.movement_pattern = "patrol"
    
    def set_follow_target(self, target):
        """Set the NPC to follow a target (usually the player)"""
        self.follow_target = target
        self.movement_pattern = "follow"
    
    def set_quest(self, quest_text, reward=None):
        """Set a quest for this NPC to give to the player"""
        self.has_quest = True
        self.quest_text = quest_text
        self.quest_reward = reward
    
    def complete_quest(self):
        """Mark the NPC's quest as completed"""
        if self.has_quest and not self.quest_completed:
            self.quest_completed = True
            return self.quest_reward
        return None
    
    def add_item(self, item):
        """Add an item to the NPC's inventory"""
        self.items.append(item)
    
    def give_item(self, item_name):
        """Give an item to the player"""
        for item in self.items[:]:
            if item["name"] == item_name:
                self.items.remove(item)
                return item
        return None
    
    def can_interact(self, player_x, player_y):
        """Check if player is in range to interact"""
        # Check if player is in range
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        current_time = pygame.time.get_ticks()
        cooldown_passed = current_time - self.last_interaction_time > self.interaction_cooldown
        
        return distance < self.interaction_range and cooldown_passed
    
    def interact(self):
        """Interact with the NPC and get dialogue"""
        self.last_interaction_time = pygame.time.get_ticks()
        self.state = "talking"
        
        # If NPC has a quest and it hasn't been given yet
        if self.has_quest and not self.quest_given:
            self.quest_given = True
            return {
                "type": "quest",
                "text": self.quest_text,
                "speaker": self.name,
                "npc_type": self.npc_type
            }
        
        # Regular dialogue
        dialogue = self.dialogue_lines[self.current_dialogue_index]
        self.current_dialogue_index = (self.current_dialogue_index + 1) % len(self.dialogue_lines)
        
        return {
            "type": "dialogue",
            "text": dialogue,
            "speaker": self.name,
            "npc_type": self.npc_type
        }
    
    def update_movement(self):
        """Update NPC movement based on movement pattern"""
        if self.movement_pattern == "stationary":
            return
        
        elif self.movement_pattern == "patrol" and self.patrol_points:
            # Move towards current patrol point
            target_x, target_y = self.patrol_points[self.current_patrol_point]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = max(1, math.sqrt(dx*dx + dy*dy))
            
            # If close enough to current point, move to next point
            if distance < 10:
                self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
                return
            
            # Move towards point
            self.x += (dx / distance) * self.movement_speed
            self.y += (dy / distance) * self.movement_speed
            
            # Update direction
            if dx > 0:
                self.direction = "right"
            elif dx < 0:
                self.direction = "left"
            
            self.is_moving = True
            self.state = "moving"
        
        elif self.movement_pattern == "follow" and hasattr(self, 'follow_target'):
            # Get target position
            target_x = self.follow_target.x
            target_y = self.follow_target.y
            
            # Calculate distance
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Only follow if beyond follow distance
            if distance > self.follow_distance:
                # Move towards target
                self.x += (dx / distance) * self.movement_speed
                self.y += (dy / distance) * self.movement_speed
                
                # Update direction
                if dx > 0:
                    self.direction = "right"
                elif dx < 0:
                    self.direction = "left"
                
                self.is_moving = True
                self.state = "moving"
            else:
                self.is_moving = False
                self.state = "idle"
    
    def update_animation(self):
        """Update animation frames"""
        if self.is_moving:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_animation_update > self.animation_cooldown:
                self.last_animation_update = current_time
                self.animation_frame = (self.animation_frame + 1) % 4  # Assuming 4 frames
    
    def update(self):
        """Update NPC state"""
        self.update_movement()
        self.update_animation()
        
        # Reset talking state after a delay
        if self.state == "talking" and pygame.time.get_ticks() - self.last_interaction_time > 1000:
            self.state = "idle"
    
    def draw(self, surface):
        """Draw the NPC"""
        if self.sprite:
            # Draw sprite with direction
            sprite_to_draw = self.sprite
            if self.direction == "left":
                sprite_to_draw = pygame.transform.flip(self.sprite, True, False)
            surface.blit(sprite_to_draw, (self.x, self.y))
        else:
            # Draw placeholder rectangle
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw interaction indicator if in talking state
        if self.state == "talking":
            pygame.draw.circle(surface, (255, 255, 255), 
                              (int(self.x + self.width/2), int(self.y - 10)), 
                              5)
        
        # Draw quest indicator if NPC has a quest
        if self.has_quest and not self.quest_completed:
            # Yellow exclamation mark
            pygame.draw.rect(surface, (255, 255, 0), 
                             (self.x + self.width/2 - 2, self.y - 25, 4, 15))
            pygame.draw.circle(surface, (255, 255, 0), 
                               (int(self.x + self.width/2), int(self.y - 30)), 
                               4)
        
        # Draw quest completed indicator
        if self.quest_completed:
            # Green check mark
            pygame.draw.line(surface, (0, 255, 0), 
                             (self.x + self.width/2 - 5, self.y - 20),
                             (self.x + self.width/2, self.y - 15), 3)
            pygame.draw.line(surface, (0, 255, 0), 
                             (self.x + self.width/2, self.y - 15),
                             (self.x + self.width/2 + 8, self.y - 25), 3)


class DialogueSystem:
    """System to manage NPC dialogues and interactions"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.SysFont('Arial', 24)
        self.dialogue_font = pygame.font.SysFont('Arial', 20)
        
        # Active dialogue
        self.active = False
        self.current_dialogue = ""
        self.current_speaker = ""
        self.current_npc_type = ""
        self.dialogue_type = "dialogue"  # dialogue, quest, item
        
        # Dialogue box properties
        self.box_width = screen_width - 100
        self.box_height = 150
        self.box_x = 50
        self.box_y = screen_height - 200
        
        # Text animation
        self.text_animation_index = 0
        self.text_animation_speed = 2  # characters per update tick
        self.text_animation_active = False
        self.last_animation_update = 0
        
        # Response options
        self.response_options = []
        self.selected_response = 0
        
        # Quest tracking
        self.active_quests = []
        self.completed_quests = []
        
        # Portrait images for different NPC types
        self.portraits = {}
        self.load_portraits()
    
    def load_portraits(self):
        """Load portrait images for different NPC types"""
        npc_types = ["soldier", "tech_priest", "inquisitor", "commissar", "civilian", "servitor"]
        for npc_type in npc_types:
            try:
                portrait_path = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)), 
                    "assets", 
                    f"{npc_type}_portrait.png"
                )
                if os.path.exists(portrait_path):
                    self.portraits[npc_type] = pygame.image.load(portrait_path).convert_alpha()
                    self.portraits[npc_type] = pygame.transform.scale(self.portraits[npc_type], (80, 80))
            except pygame.error:
                print(f"Unable to load portrait for {npc_type}")
                # Create placeholder portrait
                portrait = pygame.Surface((80, 80), pygame.SRCALPHA)
                portrait.fill((100, 100, 100))
                self.portraits[npc_type] = portrait
    
    def start_dialogue(self, dialogue_data):
        """Start a dialogue interaction"""
        self.active = True
        self.current_dialogue = dialogue_data["text"]
        self.current_speaker = dialogue_data["speaker"]
        self.current_npc_type = dialogue_data.get("npc_type", "")
        self.dialogue_type = dialogue_data.get("type", "dialogue")
        
        # Start text animation
        self.text_animation_index = 0
        self.text_animation_active = True
        self.last_animation_update = pygame.time.get_ticks()
        
        # Set response options if provided
        self.response_options = dialogue_data.get("responses", [])
        self.selected_response = 0
        
        # Add quest to active quests if this is a quest dialogue
        if self.dialogue_type == "quest" and "quest_id" in dialogue_data:
            self.active_quests.append({
                "id": dialogue_data["quest_id"],
                "title": dialogue_data.get("quest_title", "New Quest"),
                "description": dialogue_data["text"],
                "giver": dialogue_data["speaker"],
                "completed": False
            })
    
    def end_dialogue(self):
        """End the current dialogue"""
        self.active = False
        self.text_animation_active = False
        # Return the index of the selected response (or -1 if none)
        return self.selected_response if self.response_options else -1
    
    def select_next_response(self):
        """Select the next response option"""
        if self.response_options:
            self.selected_response = (self.selected_response + 1) % len(self.response_options)
    
    def select_prev_response(self):
        """Select the previous response option"""
        if self.response_options:
            self.selected_response = (self.selected_response - 1) % len(self.response_options)
    
    def complete_quest(self, quest_id):
        """Mark a quest as completed"""
        for quest in self.active_quests:
            if quest["id"] == quest_id and not quest["completed"]:
                quest["completed"] = True
                self.completed_quests.append(quest)
                self.active_quests.remove(quest)
                break
    
    def update(self):
        """Update the dialogue system (e.g., text animation)"""
        if not self.active:
            return
        current_time = pygame.time.get_ticks()
        
        # Animate text
        if self.text_animation_active:
            # You can adjust the update interval here (e.g., every 50 ms)
            if current_time - self.last_animation_update > 50:
                self.last_animation_update = current_time
                self.text_animation_index += self.text_animation_speed
                if self.text_animation_index >= len(self.current_dialogue):
                    self.text_animation_index = len(self.current_dialogue)
                    self.text_animation_active = False
    
    def draw(self, surface):
        """Draw the dialogue box and text if active"""
        if not self.active:
            return
        
        # Draw the background box
        pygame.draw.rect(surface, (0, 0, 0), 
                         (self.box_x, self.box_y, self.box_width, self.box_height))
        pygame.draw.rect(surface, (255, 255, 255), 
                         (self.box_x, self.box_y, self.box_width, self.box_height), 2)
        
        # Draw the speaker name
        speaker_surface = self.title_font.render(self.current_speaker, True, (255, 255, 255))
        surface.blit(speaker_surface, (self.box_x + 10, self.box_y + 10))
        
        # Draw the portrait if available
        if self.current_npc_type in self.portraits:
            surface.blit(self.portraits[self.current_npc_type],
                         (self.box_x + self.box_width - 90, self.box_y + 10))
        
        # Partially reveal the dialogue text (animation)
        displayed_text = self.current_dialogue[:int(self.text_animation_index)]
        text_surface = self.dialogue_font.render(displayed_text, True, (255, 255, 255))
        surface.blit(text_surface, (self.box_x + 10, self.box_y + 50))
        
        # If there are multiple response options, show them
        if self.response_options:
            y_offset = 80
            for i, option in enumerate(self.response_options):
                color = (255, 255, 0) if i == self.selected_response else (200, 200, 200)
                option_surface = self.dialogue_font.render(option, True, color)
                surface.blit(option_surface, (self.box_x + 20, self.box_y + y_offset))
                y_offset += 25
