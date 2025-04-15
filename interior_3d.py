import pygame
import os
import math
import random

# Load images
def load_image(filename, scale=None):
    try:
        image = pygame.image.load(filename).convert_alpha()
        if scale:
            image = pygame.transform.scale(image, scale)
        return image
    except pygame.error:
        print(f"Unable to load image: {filename}")
        # Return a colored surface as fallback
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        surf.fill((255, 0, 255))  # Magenta for missing textures
        return surf

class Interior3D:
    """Class to create a 3D-looking interior from a 2D image"""
    def __init__(self, background_image_path, screen_width, screen_height):
        self.original_bg = load_image(background_image_path)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.bg = pygame.transform.scale(self.original_bg, (screen_width, screen_height))
        
        # Perspective elements
        self.floor_tiles = []
        self.wall_segments = []
        self.ceiling_elements = []
        self.pillars = []
        self.graffiti = []
        self.light_sources = []
        
        # Generate 3D elements
        self.generate_floor_tiles()
        self.generate_wall_segments()
        self.generate_ceiling_elements()
        self.generate_pillars()
        
        # Lighting effects
        self.ambient_light = 0.7  # Base light level (0-1)
        self.light_flicker = 0.05  # Amount of random flicker
        self.last_flicker_time = 0
        self.flicker_interval = 100  # ms
        
        # Fog effect
        self.fog_surfaces = []
        self.generate_fog()
        
    def generate_floor_tiles(self):
        """Generate 3D-looking floor tiles"""
        tile_width = 80
        tile_height = 40
        rows = 10
        cols = 12
        
        # Starting position for the grid (perspective)
        start_x = self.screen_width // 2
        start_y = self.screen_height - 100
        
        # Perspective scaling factors
        scale_x = 1.5
        scale_y = 1.5
        
        for row in range(rows):
            for col in range(cols):
                # Calculate tile position with perspective
                perspective_factor = (row + 1) / rows
                x = start_x + (col - cols/2) * tile_width * perspective_factor * scale_x
                y = start_y - row * tile_height * perspective_factor * scale_y
                
                # Calculate tile size with perspective
                width = tile_width * perspective_factor
                height = tile_height * perspective_factor
                
                # Alternate tile colors for checkerboard effect
                if (row + col) % 2 == 0:
                    color = (80, 80, 80, 150)  # Dark gray with transparency
                else:
                    color = (100, 100, 100, 150)  # Light gray with transparency
                
                self.floor_tiles.append({
                    "rect": pygame.Rect(x, y, width, height),
                    "color": color,
                    "perspective_factor": perspective_factor
                })
    
    def generate_wall_segments(self):
        """Generate 3D-looking wall segments"""
        # Left wall
        for i in range(10):
            perspective_factor = (i + 1) / 10
            height = 300 * perspective_factor
            y = self.screen_height // 2 - height // 2
            width = 20 * perspective_factor
            x = 100 + i * 20
            
            self.wall_segments.append({
                "rect": pygame.Rect(x, y, width, height),
                "color": (120, 120, 120, 150),
                "perspective_factor": perspective_factor,
                "side": "left"
            })
        
        # Right wall
        for i in range(10):
            perspective_factor = (i + 1) / 10
            height = 300 * perspective_factor
            y = self.screen_height // 2 - height // 2
            width = 20 * perspective_factor
            x = self.screen_width - 100 - i * 20 - width
            
            self.wall_segments.append({
                "rect": pygame.Rect(x, y, width, height),
                "color": (120, 120, 120, 150),
                "perspective_factor": perspective_factor,
                "side": "right"
            })
    
    def generate_ceiling_elements(self):
        """Generate 3D-looking ceiling elements"""
        # Arches
        for i in range(5):
            perspective_factor = (i + 1) / 5
            width = self.screen_width * 0.8 * perspective_factor
            height = 40 * perspective_factor
            x = self.screen_width // 2 - width // 2
            y = 100 + i * 30
            
            self.ceiling_elements.append({
                "rect": pygame.Rect(x, y, width, height),
                "color": (100, 100, 100, 150),
                "perspective_factor": perspective_factor,
                "type": "arch"
            })
        
        # Hanging elements (chains, banners, etc.)
        for _ in range(8):
            x = random.randint(self.screen_width // 4, self.screen_width * 3 // 4)
            length = random.randint(50, 150)
            width = random.randint(5, 20)
            
            self.ceiling_elements.append({
                "rect": pygame.Rect(x, 100, width, length),
                "color": (80, 80, 80, 200),
                "perspective_factor": 1.0,
                "type": "hanging"
            })
    
    def generate_pillars(self):
        """Generate 3D-looking pillars"""
        # Create pairs of pillars along the hall
        for i in range(4):
            perspective_factor = (i + 1) / 4
            height = 400 * perspective_factor
            width = 40 * perspective_factor
            
            # Left pillar
            x_left = 150 + i * 50
            y = self.screen_height // 2 - height // 2
            
            self.pillars.append({
                "rect": pygame.Rect(x_left, y, width, height),
                "color": (90, 90, 90, 200),
                "perspective_factor": perspective_factor,
                "side": "left"
            })
            
            # Right pillar
            x_right = self.screen_width - 150 - i * 50 - width
            
            self.pillars.append({
                "rect": pygame.Rect(x_right, y, width, height),
                "color": (90, 90, 90, 200),
                "perspective_factor": perspective_factor,
                "side": "right"
            })
    
    def add_graffiti(self, text, position, color=(255, 0, 0), size=20):
        """Add arcane graffiti to the walls"""
        self.graffiti.append({
            "text": text,
            "position": position,
            "color": color,
            "size": size,
            "angle": random.randint(-10, 10)
        })
    
    def add_light_source(self, position, color=(255, 200, 100), radius=100, intensity=0.8):
        """Add a light source to the environment"""
        self.light_sources.append({
            "position": position,
            "color": color,
            "radius": radius,
            "intensity": intensity,
            "flicker": random.uniform(0.9, 1.1)  # Individual flicker factor
        })
    
    def generate_fog(self):
        """Generate fog effect surfaces"""
        for _ in range(5):
            fog_surf = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            for _ in range(100):
                x = random.randint(0, self.screen_width)
                y = random.randint(0, self.screen_height)
                radius = random.randint(20, 100)
                alpha = random.randint(5, 30)
                pygame.draw.circle(fog_surf, (200, 200, 220, alpha), (x, y), radius)
            
            self.fog_surfaces.append({
                "surface": fog_surf,
                "x": 0,
                "y": 0,
                "speed": random.uniform(0.1, 0.3)
            })
    
    def update_lighting(self):
        """Update lighting effects"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_flicker_time > self.flicker_interval:
            self.last_flicker_time = current_time
            # Update light flicker
            for light in self.light_sources:
                light["flicker"] = random.uniform(0.9, 1.1)
    
    def update_fog(self):
        """Update fog movement"""
        for fog in self.fog_surfaces:
            fog["x"] += fog["speed"]
            if fog["x"] > self.screen_width:
                fog["x"] = -self.screen_width
    
    def draw(self, surface):
        """Draw the 3D interior environment"""
        # Draw base background
        surface.blit(self.bg, (0, 0))
        
        # Draw floor tiles
        for tile in self.floor_tiles:
            s = pygame.Surface((tile["rect"].width, tile["rect"].height), pygame.SRCALPHA)
            s.fill(tile["color"])
            surface.blit(s, (tile["rect"].x, tile["rect"].y))
        
        # Draw wall segments
        for wall in self.wall_segments:
            s = pygame.Surface((wall["rect"].width, wall["rect"].height), pygame.SRCALPHA)
            s.fill(wall["color"])
            surface.blit(s, (wall["rect"].x, wall["rect"].y))
        
        # Draw pillars
        for pillar in self.pillars:
            s = pygame.Surface((pillar["rect"].width, pillar["rect"].height), pygame.SRCALPHA)
            s.fill(pillar["color"])
            surface.blit(s, (pillar["rect"].x, pillar["rect"].y))
        
        # Draw ceiling elements
        for element in self.ceiling_elements:
            s = pygame.Surface((element["rect"].width, element["rect"].height), pygame.SRCALPHA)
            s.fill(element["color"])
            surface.blit(s, (element["rect"].x, element["rect"].y))
        
        # Draw graffiti
        for g in self.graffiti:
            font = pygame.font.SysFont('Arial', g["size"])
            text_surface = font.render(g["text"], True, g["color"])
            # Rotate text if needed
            if g["angle"] != 0:
                text_surface = pygame.transform.rotate(text_surface, g["angle"])
            surface.blit(text_surface, g["position"])
        
        # Draw light sources
        for light in self.light_sources:
            # Create a radial gradient for the light
            light_surf = pygame.Surface((light["radius"]*2, light["radius"]*2), pygame.SRCALPHA)
            
            # Adjust intensity with flicker
            intensity = light["intensity"] * light["flicker"]
            
            # Draw radial gradient
            for radius in range(light["radius"], 0, -1):
                alpha = int(255 * (radius/light["radius"]) * intensity)
                color = (light["color"][0], light["color"][1], light["color"][2], 255 - alpha)
                pygame.draw.circle(light_surf, color, (light["radius"], light["radius"]), radius)
            
            # Blit light surface
            surface.blit(light_surf, (light["position"][0] - light["radius"], 
                                     light["position"][1] - light["radius"]), 
                        special_flags=pygame.BLEND_ADD)
        
        # Draw fog
        for fog in self.fog_surfaces:
            surface.blit(fog["surface"], (fog["x"], fog["y"]), special_flags=pygame.BLEND_ADD)
            # Draw a second copy for seamless scrolling
            surface.blit(fog["surface"], (fog["x"] - self.screen_width, fog["y"]), special_flags=pygame.BLEND_ADD)
    
    def update(self):
        """Update all dynamic elements"""
        self.update_lighting()
        self.update_fog()

# Example usage:
# interior = Interior3D("assets/gothic_hall.png", 800, 600)
# interior.add_graffiti("The Emperor Protects", (300, 200), (255, 215, 0))
# interior.add_light_source((400, 300), (255, 200, 100), 150)
# 
# # In game loop:
# interior.update()
# interior.draw(screen)
