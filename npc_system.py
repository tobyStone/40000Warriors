import pygame
import os
import random
import math
import sys


def create_npc(npc_type, x, y, name):
    return NPC(npc_type, x, y, name)



class NPC:
    """Class for non-player characters in the game"""
    def __init__(self, npc_type, x, y, name=None, width=40, height=60):
        self.npc_type = npc_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name or f"{npc_type.capitalize()} {random.randint(1, 100)}"
        
        # Movement properties
        self.speed = 1
        self.direction = "idle"
        self.movement_pattern = "stationary"  # stationary, patrol, follow, random
        self.patrol_points = []
        self.current_patrol_point = 0
        
        # Appearance
        self.color = self.get_color_for_type()
        self.sprite = None
        self.load_sprite(f"{npc_type}.png")
        
        # Dialogue and interaction
        self.dialogue = self.get_default_dialogue()
        self.is_talking = False
        self.interaction_range = 100
        self.abilities = self.get_abilities_for_type()
        self.cooldowns = {ability: 0 for ability in self.abilities}
        self.health = 100
        self.max_health = 100
        self.is_friendly = True
        self.quest_giver = False
        self.quest_completed = False
        self.current_quest = None
    
    def get_color_for_type(self):
        """Get color based on NPC type"""
        colors = {
            "soldier": (0, 100, 0),      # Dark green
            "tech_priest": (150, 0, 0),  # Dark red
            "inquisitor": (100, 0, 100), # Purple
            "commissar": (50, 50, 50),   # Dark gray
            "civilian": (200, 150, 100), # Tan
            "servitor": (100, 100, 150)  # Blue-gray
        }
        return colors.get(self.npc_type, (200, 200, 200))
    
    def get_abilities_for_type(self):
        """Get special abilities based on NPC type"""
        abilities = {
            "soldier": ["heal_player", "provide_ammo", "call_reinforcements"],
            "tech_priest": ["repair_equipment", "upgrade_weapons", "hack_systems"],
            "inquisitor": ["reveal_secrets", "grant_blessing", "summon_help"],
            "commissar": ["boost_morale", "order_attack", "execute_order"],
            "civilian": ["provide_info", "hide_player", "give_supplies"],
            "servitor": ["repair_armor", "scan_area", "activate_defenses"]
        }
        return abilities.get(self.npc_type, [])
    
    def get_default_dialogue(self):
        """Get default dialogue based on NPC type"""
        dialogues = {
            "soldier": [
                "The Emperor protects!",
                "We must hold this position!",
                "Need ammo? I've got some to spare.",
                "The xenos are everywhere!",
                "Stay alert, brother!"
            ],
            "tech_priest": [
                "01010100 01101000 01100101 00100000 01001111 01101101 01101110 01101001 01110011 01110011 01101001 01100001 01101000 00100000 01110111 01101001 01101100 01101100 01110011 00100000 01101001 01110100",
                "Your weapons require maintenance.",
                "The machine spirit is restless.",
                "I can enhance your equipment.",
                "The Omnissiah guides us."
            ],
            "inquisitor": [
                "The Emperor's will be done.",
                "I sense heresy nearby.",
                "Your service is noted, soldier.",
                "The xenos threat must be purged.",
                "Trust in the Emperor's wisdom."
            ],
            "commissar": [
                "For the Emperor!",
                "No retreat! No surrender!",
                "Failure is not an option!",
                "The penalty for cowardice is death!",
                "Stand firm, soldiers!"
            ],
            "civilian": [
                "Please help us!",
                "The xenos are coming!",
                "We need protection!",
                "Thank the Emperor you're here!",
                "Is it safe to come out?"
            ],
            "servitor": [
                "01010011 01110100 01100001 01110100 01110101 01110011 00100000 01110010 01100101 01110000 01101111 01110010 01110100",
                "Maintenance protocols engaged.",
                "Scanning... scanning...",
                "Systems nominal.",
                "Awaiting commands."
            ]
        }
        return dialogues.get(self.npc_type, ["Greetings, citizen."])
    
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
            print(f"Unable to load NPC sprite: {filename}")
            print(f"Error: {e}")
            print(f"Attempted path: {path}")
            # Create a placeholder sprite
            self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.sprite.fill(self.color)

    def load_npc_sprite(self, sprite_name):
        """Load a sprite for the NPC"""
        try:
            # Get the project root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            
            # Construct the path to the sprite
            path = os.path.join(project_root, "40000Warriors", "assets", sprite_name)
            
            # Load and return the sprite
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load NPC sprite: {sprite_name}")
            print(f"Error: {e}")
            print(f"Attempted path: {path}")
            # Return a colored placeholder surface
            surface = pygame.Surface((64, 64), pygame.SRCALPHA)
            surface.fill((0, 128, 0))  # Green for missing NPC textures
            pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)  # Black border
            return surface
    
    def update(self, player_x=None, player_y=None):
        """Update NPC state and position"""
        # Update cooldowns
        current_time = pygame.time.get_ticks()
        for ability in self.cooldowns:
            if self.cooldowns[ability] > 0:
                self.cooldowns[ability] = max(0, self.cooldowns[ability] - (current_time - self.last_update_time))
        
        # Handle movement based on pattern
        if self.movement_pattern == "patrol" and self.patrol_points:
            target_x, target_y = self.patrol_points[self.current_patrol_point]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 5:
                self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                
                if dx > 0:
                    self.direction = "right"
                elif dx < 0:
                    self.direction = "left"
        
        elif self.movement_pattern == "follow" and player_x is not None and player_y is not None:
            dx = player_x - self.x
            dy = player_y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > self.interaction_range:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                
                if dx > 0:
                    self.direction = "right"
                elif dx < 0:
                    self.direction = "left"
        
        elif self.movement_pattern == "random":
            if random.random() < 0.02:  # 2% chance to change direction
                self.direction = random.choice(["left", "right", "up", "down", "idle"])
            
            if self.direction == "left":
                self.x -= self.speed
            elif self.direction == "right":
                self.x += self.speed
            elif self.direction == "up":
                self.y -= self.speed
            elif self.direction == "down":
                self.y += self.speed
        
        self.last_update_time = current_time
    
    def use_ability(self, ability_name, target=None):
        """Use a special ability"""
        if ability_name not in self.abilities:
            return False
        
        if self.cooldowns[ability_name] > 0:
            return False
        
        # Set cooldown based on ability
        cooldown_times = {
            "heal_player": 30000,  # 30 seconds
            "provide_ammo": 60000,  # 1 minute
            "call_reinforcements": 120000,  # 2 minutes
            "repair_equipment": 45000,  # 45 seconds
            "upgrade_weapons": 90000,  # 1.5 minutes
            "hack_systems": 30000,  # 30 seconds
            "reveal_secrets": 60000,  # 1 minute
            "grant_blessing": 120000,  # 2 minutes
            "summon_help": 180000,  # 3 minutes
            "boost_morale": 30000,  # 30 seconds
            "order_attack": 45000,  # 45 seconds
            "execute_order": 60000,  # 1 minute
            "provide_info": 30000,  # 30 seconds
            "hide_player": 45000,  # 45 seconds
            "give_supplies": 60000,  # 1 minute
            "repair_armor": 30000,  # 30 seconds
            "scan_area": 45000,  # 45 seconds
            "activate_defenses": 90000  # 1.5 minutes
        }
        
        self.cooldowns[ability_name] = cooldown_times.get(ability_name, 30000)
        return True
    
    def draw(self, screen):
        """Draw the NPC"""
        if self.sprite:
            screen.blit(self.sprite, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw health bar if damaged
        if self.health < self.max_health:
            health_bar_width = 40
            health_bar_height = 5
            health_percent = self.health / self.max_health
            
            pygame.draw.rect(screen, (255, 0, 0),
                           (self.x + (self.width - health_bar_width)//2,
                            self.y - 10,
                            health_bar_width,
                            health_bar_height))
            pygame.draw.rect(screen, (0, 255, 0),
                           (self.x + (self.width - health_bar_width)//2,
                            self.y - 10,
                            health_bar_width * health_percent,
                            health_bar_height))
        
        # Draw interaction indicator if player is in range
        if self.is_talking:
            pygame.draw.circle(screen, (255, 255, 0),
                             (self.x + self.width//2, self.y - 20),
                             5)
    
    def interact(self):
        """Start interaction with the NPC"""
        self.is_talking = True
        return self.get_dialogue()
    
    def end_interaction(self):
        """End interaction with the NPC"""
        self.is_talking = False
    
    def give_quest(self, quest_data):
        """Give a quest to the player"""
        if not self.quest_giver:
            return False
        
        if self.current_quest is None:
            self.current_quest = quest_data
            return True
        
        return False
    
    def complete_quest(self):
        """Mark the current quest as completed"""
        if self.current_quest and not self.quest_completed:
            self.quest_completed = True
            return True
        return False
    
    def get_dialogue(self):
        """Get a random dialogue line"""
        return random.choice(self.dialogue)
    
    def set_dialogue(self, dialogue_list):
        """Set custom dialogue for this NPC"""
        self.dialogue = dialogue_list




class DialogueSystem:
    """System for handling NPC dialogue and player responses"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.current_dialogue = None
        self.current_speaker = None
        self.current_options = []
        self.selected_option = 0
        self.font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 24)
        self.option_font = pygame.font.SysFont('Arial', 18)
        
        # Dialogue box dimensions
        self.box_width = screen_width - 100
        self.box_height = 200
        self.box_x = (screen_width - self.box_width) // 2
        self.box_y = screen_height - self.box_height - 20
        
        # Response options
        self.option_height = 30
        self.option_padding = 10
        self.max_options = 4
    
    def start_dialogue(self, dialogue_data):
        """Start a new dialogue sequence"""
        self.active = True
        self.current_dialogue = dialogue_data
        self.current_speaker = dialogue_data.get("speaker", "Unknown")
        self.current_options = dialogue_data.get("options", [])
        self.selected_option = 0
    
    def end_dialogue(self):
        """End the current dialogue"""
        self.active = False
        self.current_dialogue = None
        self.current_speaker = None
        self.current_options = []
        self.selected_option = 0
    
    def select_next_response(self):
        """Select the next response option"""
        if self.current_options:
            self.selected_option = (self.selected_option + 1) % len(self.current_options)
    
    def select_prev_response(self):
        """Select the previous response option"""
        if self.current_options:
            self.selected_option = (self.selected_option - 1) % len(self.current_options)
    
    def get_selected_response(self):
        """Get the currently selected response"""
        if self.current_options and 0 <= self.selected_option < len(self.current_options):
            return self.current_options[self.selected_option]
        return None
    
    def draw(self, screen):
        """Draw the dialogue box and options"""
        if not self.active or not self.current_dialogue:
            return
        
        # Draw dialogue box
        pygame.draw.rect(screen, (0, 0, 0), (self.box_x, self.box_y, self.box_width, self.box_height))
        pygame.draw.rect(screen, (255, 255, 255), (self.box_x, self.box_y, self.box_width, self.box_height), 2)
        
        # Draw speaker name
        speaker_text = self.title_font.render(self.current_speaker, True, (255, 255, 255))
        screen.blit(speaker_text, (self.box_x + 10, self.box_y + 10))
        
        # Draw dialogue text
        text = self.current_dialogue.get("text", "")
        text_surface = self.font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (self.box_x + 10, self.box_y + 40))
        
        # Draw response options
        if self.current_options:
            option_y = self.box_y + 80
            for i, option in enumerate(self.current_options):
                color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
                option_text = self.option_font.render(option, True, color)
                screen.blit(option_text, (self.box_x + 20, option_y))
                option_y += self.option_height + self.option_padding

# Expose create_npc and DialogueSystem if you want to import them from elsewhere
__all__ = ["create_npc", "DialogueSystem"]