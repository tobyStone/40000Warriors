import pygame
import os
import math
import random

def load_image(filename, scale=None):
    """Load an image with optional scaling."""
    try:
        image = pygame.image.load(filename).convert_alpha()
        if scale:
            image = pygame.transform.scale(image, scale)
        return image
    except pygame.error:
        print(f"Unable to load image: {filename}")
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        surf.fill((255, 0, 255))
        return surf

class Interior3D:
    """Class to create a 3D-looking interior from a 2D image."""
    def __init__(self, background_path, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Collections for dynamic elements
        self.graffiti = []
        self.light_sources = []
        self.floor_tiles = []
        self.wall_segments = []
        self.ceiling_elements = []
        self.fog_surfaces = []
        self.pillars = []
        
        # Try to load the background
        self.bg = self.load_background(background_path)
        
        # Parallax or 3D effect parameters
        self.parallax_offset_x = 0
        self.parallax_offset_y = 0
        self.parallax_strength = 0.05
        
        # For lighting/flicker logic
        self.last_flicker_time = 0
        self.flicker_interval = 500  # e.g. flicker every 500 ms

    def load_background(self, path):
        """Attempt to load a background image from various possible paths."""
        possible_paths = [
            path,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), path),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", os.path.basename(path)),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.path.basename(path))
        ]
        
        for p in possible_paths:
            if os.path.exists(p):
                try:
                    return pygame.image.load(p).convert_alpha()
                except pygame.error:
                    pass
        
        print(f"Warning: Could not load interior background '{path}'. Using placeholder.")
        print(f"Attempted paths: {possible_paths}")
        surf = pygame.Surface((self.screen_width, self.screen_height))
        surf.fill((80, 60, 60))
        return surf

    def add_graffiti(self, text, position, color=(255, 0, 0), size=20):
        """Add a graffiti text item to the interior surface."""
        self.graffiti.append({
            "text": text,
            "position": position,
            "color": color,
            "size": size,
            "angle": random.randint(-10, 10)
        })
    
    def add_light_source(self, position, color=(255, 200, 100), radius=100, intensity=0.8):
        """Add a light source that will create a radial gradient in draw()."""
        self.light_sources.append({
            "position": position,
            "color": color,
            "radius": radius,
            "intensity": intensity,
            "flicker": random.uniform(0.9, 1.1)
        })

    def update_lighting(self):
        """Handle flicker intervals and update each light's flicker factor."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_flicker_time > self.flicker_interval:
            self.last_flicker_time = current_time
            for light in self.light_sources:
                light["flicker"] = random.uniform(0.9, 1.1)
    
    def update_fog(self):
        """Example method if you're implementing drifting fog surfaces."""
        for fog in self.fog_surfaces:
            fog["x"] += fog["speed"]
            if fog["x"] > self.screen_width:
                fog["x"] = -self.screen_width
    
    def update(self):
        """Update dynamic elements: lighting, fog, animations, etc."""
        self.update_lighting()
        self.update_fog()
    
    def draw(self, surface):
        """Draw the entire 3D interior with background, graffiti, lights, etc."""
        # Draw base background
        surface.blit(self.bg, (0, 0))
        
        # If you have code for floor_tiles, walls, pillars, etc., you'd draw them here
        # e.g.:
        # for tile in self.floor_tiles:
        #     ...
        
        # Draw graffiti
        for g in self.graffiti:
            font = pygame.font.SysFont('Arial', g["size"])
            text_surface = font.render(g["text"], True, g["color"])
            if g["angle"] != 0:
                text_surface = pygame.transform.rotate(text_surface, g["angle"])
            surface.blit(text_surface, g["position"])
        
        # Draw each light as a radial gradient
        for light in self.light_sources:
            light_surf = pygame.Surface((light["radius"] * 2, light["radius"] * 2), pygame.SRCALPHA)
            flicker_intensity = light["intensity"] * light["flicker"]
            for r in range(light["radius"], 0, -1):
                alpha = int(255 * (r / light["radius"]) * flicker_intensity)
                color = (light["color"][0], light["color"][1], light["color"][2], 255 - alpha)
                pygame.draw.circle(light_surf, color, (light["radius"], light["radius"]), r)
            surface.blit(light_surf, (light["position"][0] - light["radius"],
                                      light["position"][1] - light["radius"]),
                         special_flags=pygame.BLEND_ADD)
        
        # Draw fog if implemented
        for fog in self.fog_surfaces:
            surface.blit(fog["surface"], (fog["x"], fog["y"]), special_flags=pygame.BLEND_ADD)
            surface.blit(fog["surface"], (fog["x"] - self.screen_width, fog["y"]), special_flags=pygame.BLEND_ADD)
