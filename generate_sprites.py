import pygame
import os
import math
import random

# Initialize pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tyranid Sprite Generator")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (150, 50, 200)
DARK_PURPLE = (100, 0, 150)
LIGHT_PURPLE = (180, 80, 180)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Tyranid types and their base colors
TYRANID_COLORS = {
    "genestealer": (150, 50, 200),  # Purple
    "warrior": (100, 0, 150),       # Dark purple
    "gaunt": (180, 80, 180),        # Light purple
    "lictor": (120, 40, 120),       # Medium purple
    "carnifex": (80, 0, 100),       # Very dark purple
    "zoanthrope": (200, 100, 220)   # Bright purple
}

# Sprite sizes
SPRITE_SIZES = {
    "genestealer": (40, 40),
    "warrior": (50, 70),
    "gaunt": (30, 30),
    "lictor": (45, 70),
    "carnifex": (80, 80),
    "zoanthrope": (40, 60)
}

def safe_color(color_value):
    """Ensure color values are within valid range (0-255)"""
    return max(0, min(255, color_value))

def generate_tyranid_sprite(tyranid_type, state="idle", frame=0):
    """Generate a sprite for a specific Tyranid type and animation state"""
    width, height = SPRITE_SIZES[tyranid_type]
    base_color = TYRANID_COLORS[tyranid_type]
    
    # Create a surface with alpha channel
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Draw different shapes based on Tyranid type
    if tyranid_type == "genestealer":
        # Body
        pygame.draw.ellipse(sprite, base_color, (width//4, height//4, width//2, height//2))
        
        # Head
        head_y_offset = int(math.sin(frame * 0.5) * 2)  # Slight animation
        pygame.draw.ellipse(sprite, base_color, (width//4, height//6 + head_y_offset, width//2, height//3))
        
        # Claws
        claw_extension = int(math.sin(frame * 0.3) * 3)  # Animation for claws
        darker_color = (safe_color(base_color[0]-30), safe_color(base_color[1]-30), safe_color(base_color[2]-30))
        pygame.draw.polygon(sprite, darker_color, 
                           [(width//4, height//2), (0, height//3 + claw_extension), (width//4, height//3)])
        pygame.draw.polygon(sprite, darker_color, 
                           [(3*width//4, height//2), (width, height//3 + claw_extension), (3*width//4, height//3)])
        
        # Legs
        leg_extension = int(math.sin(frame * 0.4) * 2)  # Animation for legs
        leg_color = (safe_color(base_color[0]-20), safe_color(base_color[1]-20), safe_color(base_color[2]-20))
        pygame.draw.line(sprite, leg_color, 
                        (width//3, 2*height//3), (width//4, height-5 + leg_extension), 2)
        pygame.draw.line(sprite, leg_color, 
                        (2*width//3, 2*height//3), (3*width//4, height-5 + leg_extension), 2)
        
        # Eyes (red)
        pygame.draw.circle(sprite, RED, (width//3, height//4), 2)
        pygame.draw.circle(sprite, RED, (2*width//3, height//4), 2)
        
    elif tyranid_type == "warrior":
        # Body
        pygame.draw.ellipse(sprite, base_color, (width//4, height//3, width//2, height//3))
        
        # Head
        head_y_offset = int(math.sin(frame * 0.3) * 2)  # Slight animation
        pygame.draw.ellipse(sprite, base_color, (width//4, height//6 + head_y_offset, width//2, height//4))
        
        # Tail
        tail_swing = int(math.sin(frame * 0.2) * 3)  # Animation for tail
        tail_color = (safe_color(base_color[0]-20), safe_color(base_color[1]-20), safe_color(base_color[2]-20))
        pygame.draw.polygon(sprite, tail_color, 
                           [(width//2, 2*height//3), (width//2 + tail_swing, height-5), (width//2 - tail_swing, height-5)])
        
        # Arms with weapons
        arm_extension = int(math.sin(frame * 0.3) * 2)  # Animation for arms
        arm_color = (safe_color(base_color[0]-30), safe_color(base_color[1]-30), safe_color(base_color[2]-30))
        pygame.draw.line(sprite, arm_color, 
                        (width//4, height//2), (0, height//2 + arm_extension), 3)
        pygame.draw.line(sprite, arm_color, 
                        (3*width//4, height//2), (width, height//2 + arm_extension), 3)
        
        # Legs
        leg_extension = int(math.sin(frame * 0.4) * 2)  # Animation for legs
        leg_color = (safe_color(base_color[0]-20), safe_color(base_color[1]-20), safe_color(base_color[2]-20))
        pygame.draw.line(sprite, leg_color, 
                        (width//3, 2*height//3), (width//4, height-5 + leg_extension), 2)
        pygame.draw.line(sprite, leg_color, 
                        (2*width//3, 2*height//3), (3*width//4, height-5 + leg_extension), 2)
        
        # Eyes (red)
        pygame.draw.circle(sprite, RED, (width//3, height//5), 2)
        pygame.draw.circle(sprite, RED, (2*width//3, height//5), 2)
        
        # Bio-weapon (green glow)
        if state == "attacking":
            pygame.draw.circle(sprite, GREEN, (0, height//2 + arm_extension), 5)
            glow_surf = pygame.Surface((14, 14), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (0, 255, 0, 128), (7, 7), 7)  # Glow effect
            sprite.blit(glow_surf, (-7, height//2 + arm_extension - 7))
        
    elif tyranid_type == "gaunt":
        # Small body
        pygame.draw.ellipse(sprite, base_color, (width//4, height//3, width//2, height//3))
        
        # Head
        head_y_offset = int(math.sin(frame * 0.5) * 1)  # Slight animation
        pygame.draw.ellipse(sprite, base_color, (width//4, height//6 + head_y_offset, width//2, height//4))
        
        # Legs (6 of them for insect-like appearance)
        leg_extension = int(math.sin(frame * 0.6) * 2)  # Animation for legs
        leg_color = (safe_color(base_color[0]-20), safe_color(base_color[1]-20), safe_color(base_color[2]-20))
        for i in range(3):
            y_pos = height//3 + (i * height//6)
            pygame.draw.line(sprite, leg_color, 
                            (width//4, y_pos), (0, y_pos + leg_extension), 1)
            pygame.draw.line(sprite, leg_color, 
                            (3*width//4, y_pos), (width, y_pos + leg_extension), 1)
        
        # Eyes (red)
        pygame.draw.circle(sprite, RED, (width//3, height//5), 1)
        pygame.draw.circle(sprite, RED, (2*width//3, height//5), 1)
        
    elif tyranid_type == "lictor":
        # Slender body
        pygame.draw.ellipse(sprite, base_color, (width//3, height//4, width//3, height//2))
        
        # Head
        head_y_offset = int(math.sin(frame * 0.3) * 2)  # Slight animation
        pygame.draw.ellipse(sprite, base_color, (width//3, height//8 + head_y_offset, width//3, height//5))
        
        # Camouflage effect if in stealth mode
        if state == "stealth":
            # Add transparency
            for y in range(height):
                for x in range(width):
                    if sprite.get_at((x, y))[3] > 0:  # If pixel is not transparent
                        color = sprite.get_at((x, y))
                        sprite.set_at((x, y), (color[0], color[1], color[2], 128))  # Half transparency
        
        # Claws (extra large)
        claw_extension = int(math.sin(frame * 0.2) * 4)  # Animation for claws
        claw_color = (safe_color(base_color[0]-30), safe_color(base_color[1]-30), safe_color(base_color[2]-30))
        pygame.draw.polygon(sprite, claw_color, 
                           [(width//4, height//2), (0, height//3 + claw_extension), (width//4, height//3)])
        pygame.draw.polygon(sprite, claw_color, 
                           [(3*width//4, height//2), (width, height//3 + claw_extension), (3*width//4, height//3)])
        
        # Legs
        leg_extension = int(math.sin(frame * 0.4) * 2)  # Animation for legs
        leg_color = (safe_color(base_color[0]-20), safe_color(base_color[1]-20), safe_color(base_color[2]-20))
        pygame.draw.line(sprite, leg_color, 
                        (width//3, 3*height//4), (width//4, height-5 + leg_extension), 2)
        pygame.draw.line(sprite, leg_color, 
                        (2*width//3, 3*height//4), (3*width//4, height-5 + leg_extension), 2)
        
        # Eyes (red)
        pygame.draw.circle(sprite, RED, (width//3, height//7), 2)
        pygame.draw.circle(sprite, RED, (2*width//3, height//7), 2)
        
    elif tyranid_type == "carnifex":
        # Large bulky body
        pygame.draw.ellipse(sprite, base_color, (width//6, height//4, 2*width//3, height//2))
        
        # Head
        head_y_offset = int(math.sin(frame * 0.2) * 2)  # Slight animation
        pygame.draw.ellipse(sprite, base_color, (width//4, height//6 + head_y_offset, width//2, height//4))
        
        # Armored carapace
        carapace_color = (safe_color(base_color[0]-40), safe_color(base_color[1]-40), safe_color(base_color[2]-40))
        pygame.draw.arc(sprite, carapace_color, 
                       (width//6, height//4, 2*width//3, height//2), 0, math.pi, 5)
        
        # Heavy claws
        claw_extension = int(math.sin(frame * 0.15) * 3)  # Animation for claws
        claw_color = (safe_color(base_color[0]-30), safe_color(base_color[1]-30), safe_color(base_color[2]-30))
        pygame.draw.polygon(sprite, claw_color, 
                           [(width//6, height//2), (0, height//2 + claw_extension), (width//6, 2*height//3)])
        pygame.draw.polygon(sprite, claw_color, 
                           [(5*width//6, height//2), (width, height//2 + claw_extension), (5*width//6, 2*height//3)])
        
        # Legs (thick)
        leg_extension = int(math.sin(frame * 0.3) * 2)  # Animation for legs
        leg_color = (safe_color(base_color[0]-20), safe_color(base_color[1]-20), safe_color(base_color[2]-20))
        pygame.draw.line(sprite, leg_color, 
                        (width//3, 2*height//3), (width//4, height-5 + leg_extension), 4)
        pygame.draw.line(sprite, leg_color, 
                        (2*width//3, 2*height//3), (3*width//4, height-5 + leg_extension), 4)
        
        # Eyes (red)
        pygame.draw.circle(sprite, RED, (width//3, height//5), 3)
        pygame.draw.circle(sprite, RED, (2*width//3, height//5), 3)
        
        # Ground pound effect
        if state == "attacking":
            shockwave_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(shockwave_surf, (255, 255, 255, 100), (20, 20), 20)  # Shockwave
            sprite.blit(shockwave_surf, (width//2 - 20, height-25))
            
            outer_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(outer_surf, (255, 255, 255, 50), (30, 30), 30)  # Outer shockwave
            sprite.blit(outer_surf, (width//2 - 30, height-35))
        
    elif tyranid_type == "zoanthrope":
        # Floating body
        pygame.draw.ellipse(sprite, base_color, (width//4, height//3, width//2, height//3))
        
        # Large head with psychic brain
        head_y_offset = int(math.sin(frame * 0.3) * 2)  # Slight animation
        pygame.draw.ellipse(sprite, base_color, (width//6, height//8 + head_y_offset, 2*width//3, height//3))
        
        # Psychic energy
        energy_pulse = int(math.sin(frame * 0.5) * 5)  # Pulsing effect
        if state == "attacking":
            # Strong psychic blast
            energy_surf = pygame.Surface((30 + energy_pulse*2, 30 + energy_pulse*2), pygame.SRCALPHA)
            pygame.draw.circle(energy_surf, (200, 100, 255, 150), (15 + energy_pulse, 15 + energy_pulse), 15 + energy_pulse)
            sprite.blit(energy_surf, (width//2 - 15 - energy_pulse, height//4 - 15 - energy_pulse))
            
            outer_surf = pygame.Surface((40 + energy_pulse*2, 40 + energy_pulse*2), pygame.SRCALPHA)
            pygame.draw.circle(outer_surf, (220, 150, 255, 100), (20 + energy_pulse, 20 + energy_pulse), 20 + energy_pulse)
            sprite.blit(outer_surf, (width//2 - 20 - energy_pulse, height//4 - 20 - energy_pulse))
        else:
            # Ambient psychic energy
            energy_surf = pygame.Surface((20 + energy_pulse*2, 20 + energy_pulse*2), pygame.SRCALPHA)
            pygame.draw.circle(energy_surf, (200, 100, 255, 100), (10 + energy_pulse, 10 + energy_pulse), 10 + energy_pulse)
            sprite.blit(energy_surf, (width//2 - 10 - energy_pulse, height//4 - 10 - energy_pulse))
        
        # Tentacles instead of legs
        tentacle_wave = int(math.sin(frame * 0.4) * 3)  # Animation for tentacles
        tentacle_color = (safe_color(base_color[0]-20), safe_color(base_color[1]-20), safe_color(base_color[2]-20))
        for i in range(3):
            x_offset = (i - 1) * width//6
            pygame.draw.line(sprite, tentacle_color, 
                            (width//2 + x_offset, 2*height//3), 
                            (width//2 + x_offset + tentacle_wave, height-5), 2)
        
        # Eyes (glowing)
        pygame.draw.circle(sprite, (255, 100, 255), (width//3, height//5), 2)
        pygame.draw.circle(sprite, (255, 100, 255), (2*width//3, height//5), 2)
    
    return sprite

def save_sprite_sheet(tyranid_type):
    """Generate and save a sprite sheet for a specific Tyranid type"""
    width, height = SPRITE_SIZES[tyranid_type]
    
    # Create sprite sheet with 4 frames for each of 3 states (idle, moving, attacking)
    sheet_width = width * 4
    sheet_height = height * 3
    
    sprite_sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
    
    # Generate sprites for each state and frame
    states = ["idle", "moving", "attacking"]
    
    for state_idx, state in enumerate(states):
        for frame in range(4):
            sprite = generate_tyranid_sprite(tyranid_type, state, frame)
            sprite_sheet.blit(sprite, (frame * width, state_idx * height))
    
    # Save the sprite sheet
    output_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(output_dir, f"{tyranid_type}_sprites.png")
    pygame.image.save(sprite_sheet, filename)
    print(f"Saved sprite sheet for {tyranid_type} to {filename}")

def generate_all_sprites():
    """Generate sprite sheets for all Tyranid types"""
    for tyranid_type in TYRANID_COLORS.keys():
        save_sprite_sheet(tyranid_type)
    print("All sprite sheets generated successfully!")

if __name__ == "__main__":
    generate_all_sprites()
    pygame.quit()
