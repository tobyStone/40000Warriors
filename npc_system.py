import pygame
import os
import random
import math
import sys

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
        
        # Dialogue
        self.dialogue = self.get_default_dialogue()
        self.is_talking = False
    
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
    
    def get_default_dialogue(self):
        """Get default dialogue based on NPC type"""
        dialogues = {
            "soldier": [
                "For the Emperor!",
                "Stand fast, brother.",
                "The xenos must be purged.",
                "We shall know no fear."
            ],
            "tech_priest": [
                "The Omnissiah guides my hand.",
                "Flesh is weak. Machine is eternal.",
                "I require more sacred oils.",
                "01010000 01110010 01100001 01101001 01110011 01100101 00100000 01110100 01101000 01100101 00100000 01001111 01101101 01101110 01101001 01110011 01110011 01101001 01100001 01101000"
            ],
            "inquisitor": [
                "Heresy grows from idleness.",
                "Innocence proves nothing.",
                "There is no such thing as innocence, only degrees of guilt.",
                "I am watching you, always."
            ],
            "commissar": [
                "Cowardice will be met with summary execution.",
                "Fight for the Emperor or die trying.",
                "Retreat? I think not.",
                "Your duty is to serve the Emperor's will."
            ],
            "civilian": [
                "Emperor protect us!",
                "Please, save us from the xenos!",
                "I've seen terrible things...",
                "Is it safe here?"
            ],
            "servitor": [
                "Awaiting instructions.",
                "*mechanical noises*",
                "How may this unit serve?",
                "Processing..."
            ]
        }
        return dialogues.get(self.npc_type, ["..."])
    
    def load_sprite(self, filename):
        """Load the sprite image"""
        try:
            # Construct the full path to the 40000Warriors folder
            project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "40000Warriors")
            )
            # Point to your 'assets/character' directory
            assets_path = os.path.join(project_root, "assets", "character")
        
            # Construct the full path to the desired sprite file
            path = os.path.join(assets_path, filename)
        
            # Now load the sprite
            self.sprite = pygame.image.load(path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (self.width, self.height))
        
        except pygame.error:
            print(f"Unable to load NPC sprite: {filename}")
            print(f"Attempted path: {path}")
            # Create a placeholder sprite
            self.sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.sprite.fill(self.color)

    
    def update(self, player_x=None, player_y=None):
        """Update NPC position and state"""
        if self.movement_pattern == "stationary":
            return
        
        if self.movement_pattern == "patrol" and self.patrol_points:
            target_x, target_y = self.patrol_points[self.current_patrol_point]
            
            # Move towards patrol point
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < 5:  # Close enough to target
                self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
            else:
                # Move towards target
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        
        elif self.movement_pattern == "follow" and player_x is not None and player_y is not None:
            # Move towards player but keep distance
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > 100:  # Only follow if player is far enough
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        
        elif self.movement_pattern == "random":
            # Random movement
            if random.random() < 0.02:  # 2% chance to change direction
                self.direction = random.choice(["up", "down", "left", "right", "idle"])
            
            if self.direction == "up":
                self.y -= self.speed
            elif self.direction == "down":
                self.y += self.speed
            elif self.direction == "left":
                self.x -= self.speed
            elif self.direction == "right":
                self.x += self.speed
    
    def draw(self, screen):
        """Draw the NPC on the screen"""
        if self.sprite:
            screen.blit(self.sprite, (self.x - self.width//2, self.y - self.height//2))
        else:
            # Draw placeholder rectangle
            pygame.draw.rect(screen, self.color, 
                            (self.x - self.width//2, self.y - self.height//2, 
                             self.width, self.height))
    
    def get_dialogue(self):
        """Get a random dialogue line"""
        return random.choice(self.dialogue)
    
    def set_dialogue(self, dialogue_list):
        """Set custom dialogue for this NPC"""
        self.dialogue = dialogue_list
    
    def interact(self):
        """Interact with this NPC"""
        self.is_talking = True
        return self.get_dialogue()
    
    def end_interaction(self):
        """End interaction with this NPC"""
        self.is_talking = False

class DialogueSystem:
    """System for handling NPC dialogues"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.current_npc = None
        self.current_text = ""
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
                    "character",
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
    
    def start_dialogue(self, npc):
        """Start dialogue with an NPC"""
        self.active = True
        self.current_npc = npc
        self.current_text = npc.interact()
    
    def end_dialogue(self):
        """End the current dialogue"""
        if self.current_npc:
            self.current_npc.end_interaction()
        self.active = False
        self.current_npc = None
        self.current_text = ""
    
    def draw(self, screen):
        """Draw the dialogue UI"""
        if not self.active or not self.current_npc:
            return
        
        # Draw dialogue box
        box_height = 150
        box_y = self.screen_height - box_height - 10
        pygame.draw.rect(screen, (50, 50, 50), 
                         (10, box_y, self.screen_width - 20, box_height))
        pygame.draw.rect(screen, (200, 200, 200), 
                         (10, box_y, self.screen_width - 20, box_height), 2)
        
        # Draw portrait
        portrait = self.portraits.get(self.current_npc.npc_type)
        if portrait:
            screen.blit(portrait, (20, box_y + 10))
        
        # Draw name
        font = pygame.font.SysFont('Arial', 24)
        name_text = font.render(self.current_npc.name, True, (255, 215, 0))
        screen.blit(name_text, (110, box_y + 15))
        
        # Draw dialogue text
        dialogue_font = pygame.font.SysFont('Arial', 18)
        lines = self.wrap_text(self.current_text, dialogue_font, self.screen_width - 150)
        for i, line in enumerate(lines):
            text_surface = dialogue_font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (110, box_y + 50 + i * 25))
        
        # Draw continue prompt
        prompt_text = dialogue_font.render("Press E to continue", True, (200, 200, 200))
        screen.blit(prompt_text, (self.screen_width - 150, box_y + box_height - 30))
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within a certain width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Test width with current word added
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                # Line is full, start a new line
                lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

def create_npc(npc_type, x, y, name=None):
    """Create and return an NPC of the specified type"""
    return NPC(npc_type, x, y, name)

