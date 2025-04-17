import pygame
import math
import random
import os
from tyranid_sprites import TyranidSprite

class BossPhase:
    """Represents a phase in a boss battle"""
    def __init__(self, name, health_threshold, abilities, duration=0):
        self.name = name
        self.health_threshold = health_threshold
        self.abilities = abilities
        self.duration = duration
        self.time_elapsed = 0
        self.active = False

class BossAbility:
    """Represents a special ability a boss can use"""
    def __init__(self, name, cooldown, damage, range, effect=None):
        self.name = name
        self.cooldown = cooldown
        self.damage = damage
        self.range = range
        self.effect = effect
        self.last_used = 0
        self.active = False

class Boss(TyranidSprite):
    """Base class for boss enemies"""
    def __init__(self, x, y, boss_type, health, damage, speed):
        super().__init__(x, y, 100, 100, boss_type, health, damage, speed)
        self.boss_type = boss_type
        self.phases = []
        self.current_phase = None
        self.abilities = []
        self.enrage_timer = 0
        self.enraged = False
        self.invulnerable = False
        self.invulnerability_timer = 0
        self.attack_patterns = []
        self.current_pattern = 0
        self.pattern_timer = 0
        self.summoned_minions = []
        self.arena_effects = []
        
        # Boss-specific properties
        self.weak_points = []
        self.shield_points = []
        self.armor_points = []
        self.damage_multiplier = 1.0
        
        # Visual effects
        self.aura_color = (255, 0, 0)
        self.aura_radius = 150
        self.aura_pulse_speed = 0.05
        self.aura_pulse_phase = 0
    
    def add_phase(self, phase):
        """Add a new phase to the boss battle"""
        self.phases.append(phase)
        if not self.current_phase:
            self.current_phase = phase
            phase.active = True
    
    def add_ability(self, ability):
        """Add a new ability to the boss"""
        self.abilities.append(ability)
    
    def update_phase(self):
        """Update the current phase of the boss battle"""
        if not self.current_phase:
            return
        
        # Check if we should transition to next phase
        health_percent = (self.health / self.max_health) * 100
        if health_percent <= self.current_phase.health_threshold:
            # Find next phase
            current_index = self.phases.index(self.current_phase)
            if current_index < len(self.phases) - 1:
                self.current_phase.active = False
                self.current_phase = self.phases[current_index + 1]
                self.current_phase.active = True
                self.on_phase_transition()
        
        # Update phase timer
        if self.current_phase.duration > 0:
            self.current_phase.time_elapsed += 1
            if self.current_phase.time_elapsed >= self.current_phase.duration:
                self.on_phase_timeout()
    
    def update_abilities(self):
        """Update boss abilities and cooldowns"""
        current_time = pygame.time.get_ticks()
        for ability in self.abilities:
            if current_time - ability.last_used >= ability.cooldown:
                ability.active = True
    
    def use_ability(self, ability_name, target=None):
        """Use a specific ability"""
        for ability in self.abilities:
            if ability.name == ability_name and ability.active:
                ability.last_used = pygame.time.get_ticks()
                ability.active = False
                return True
        return False
    
    def update(self):
        """Update boss state"""
        super().update()
        
        # Update phase
        self.update_phase()
        
        # Update abilities
        self.update_abilities()
        
        # Update attack pattern
        self.update_attack_pattern()
        
        # Update minions
        self.update_minions()
        
        # Update arena effects
        self.update_arena_effects()
        
        # Update visual effects
        self.aura_pulse_phase += self.aura_pulse_speed
        if self.aura_pulse_phase > 2 * math.pi:
            self.aura_pulse_phase = 0
    
    def update_attack_pattern(self):
        """Update the current attack pattern"""
        if not self.attack_patterns:
            return
        
        self.pattern_timer += 1
        if self.pattern_timer >= self.attack_patterns[self.current_pattern]["duration"]:
            self.current_pattern = (self.current_pattern + 1) % len(self.attack_patterns)
            self.pattern_timer = 0
    
    def update_minions(self):
        """Update summoned minions"""
        for minion in self.summoned_minions[:]:
            if not minion.is_alive:
                self.summoned_minions.remove(minion)
            else:
                minion.update()
    
    def update_arena_effects(self):
        """Update arena-wide effects"""
        for effect in self.arena_effects[:]:
            if effect["duration"] <= 0:
                self.arena_effects.remove(effect)
            else:
                effect["duration"] -= 1
    
    def draw(self, surface):
        """Draw the boss and its effects"""
        # Draw aura
        pulse_radius = self.aura_radius + math.sin(self.aura_pulse_phase) * 20
        aura_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surface, (*self.aura_color, 50),
                         (pulse_radius, pulse_radius), pulse_radius)
        surface.blit(aura_surface,
                    (self.x + self.width//2 - pulse_radius,
                     self.y + self.height//2 - pulse_radius))
        
        # Draw boss
        super().draw(surface)
        
        # Draw minions
        for minion in self.summoned_minions:
            minion.draw(surface)
        
        # Draw arena effects
        for effect in self.arena_effects:
            if "draw" in effect:
                effect["draw"](surface)
        
        # Draw phase indicator
        if self.current_phase:
            phase_text = pygame.font.SysFont('Arial', 24).render(
                f"Phase: {self.current_phase.name}", True, (255, 255, 255))
            surface.blit(phase_text, (10, 10))
    
    def on_phase_transition(self):
        """Called when transitioning to a new phase"""
        # Reset timers and patterns
        self.pattern_timer = 0
        self.current_pattern = 0
        
        # Clear minions and effects
        self.summoned_minions.clear()
        self.arena_effects.clear()
        
        # Update boss properties based on phase
        if self.current_phase.name == "Enraged":
            self.enraged = True
            self.damage_multiplier = 2.0
            self.speed *= 1.5
    
    def on_phase_timeout(self):
        """Called when a timed phase ends"""
        # Handle phase timeout logic
        pass

    def load_boss_sprite(self, sprite_name):
        """Load a sprite for the boss"""
        try:
            # Get the project root directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            
            # Construct the path to the sprite
            path = os.path.join(project_root, "40000Warriors", "assets", sprite_name)
            
            # Load and return the sprite
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load boss sprite: {sprite_name}")
            print(f"Error: {e}")
            print(f"Attempted path: {path}")
            # Return a colored placeholder surface
            surface = pygame.Surface((128, 128), pygame.SRCALPHA)
            surface.fill((128, 0, 128))  # Purple for missing boss textures
            pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 3)  # Black border
            return surface

class HiveTyrantBoss(Boss):
    """Specialized boss version of the Hive Tyrant"""
    def __init__(self, x, y):
        super().__init__(x, y, "hive_tyrant_boss", 1000, 50, 3)
        
        # Add phases
        self.add_phase(BossPhase("Normal", 100, ["psychic_scream", "summon_guards"]))
        self.add_phase(BossPhase("Enraged", 50, ["psychic_storm", "mass_summon"]))
        self.add_phase(BossPhase("Final", 25, ["psychic_apocalypse", "endless_swarm"]))
        
        # Add abilities
        self.add_ability(BossAbility("psychic_scream", 5000, 30, 200))
        self.add_ability(BossAbility("summon_guards", 10000, 0, 0))
        self.add_ability(BossAbility("psychic_storm", 8000, 40, 300))
        self.add_ability(BossAbility("mass_summon", 15000, 0, 0))
        self.add_ability(BossAbility("psychic_apocalypse", 12000, 60, 400))
        self.add_ability(BossAbility("endless_swarm", 20000, 0, 0))
        
        # Set up attack patterns
        self.attack_patterns = [
            {"name": "normal", "duration": 300, "abilities": ["psychic_scream"]},
            {"name": "summoning", "duration": 200, "abilities": ["summon_guards"]},
            {"name": "rest", "duration": 100, "abilities": []}
        ]
        
        # Set up weak points
        self.weak_points = [
            {"x": self.x + 20, "y": self.y + 20, "width": 20, "height": 20},
            {"x": self.x + 60, "y": self.y + 20, "width": 20, "height": 20}
        ]
        
        # Set up shield points
        self.shield_points = [
            {"x": self.x + 40, "y": self.y + 40, "width": 20, "height": 20, "health": 100}
        ]

class SwarmlordBoss(Boss):
    """Specialized boss version of the Swarmlord"""
    def __init__(self, x, y):
        super().__init__(x, y, "swarmlord_boss", 1500, 75, 4)
        
        # Add phases
        self.add_phase(BossPhase("Normal", 100, ["bone_sword_sweep", "hive_guard_summon"]))
        self.add_phase(BossPhase("Enraged", 60, ["bone_sword_storm", "tyrant_guard_summon"]))
        self.add_phase(BossPhase("Final", 30, ["bone_sword_apocalypse", "hive_tyrant_summon"]))
        
        # Add abilities
        self.add_ability(BossAbility("bone_sword_sweep", 4000, 40, 150))
        self.add_ability(BossAbility("hive_guard_summon", 12000, 0, 0))
        self.add_ability(BossAbility("bone_sword_storm", 6000, 60, 200))
        self.add_ability(BossAbility("tyrant_guard_summon", 15000, 0, 0))
        self.add_ability(BossAbility("bone_sword_apocalypse", 10000, 80, 250))
        self.add_ability(BossAbility("hive_tyrant_summon", 20000, 0, 0))
        
        # Set up attack patterns
        self.attack_patterns = [
            {"name": "melee", "duration": 200, "abilities": ["bone_sword_sweep"]},
            {"name": "summoning", "duration": 150, "abilities": ["hive_guard_summon"]},
            {"name": "rest", "duration": 100, "abilities": []}
        ]
        
        # Set up weak points
        self.weak_points = [
            {"x": self.x + 30, "y": self.y + 30, "width": 20, "height": 20},
            {"x": self.x + 50, "y": self.y + 30, "width": 20, "height": 20}
        ]
        
        # Set up armor points
        self.armor_points = [
            {"x": self.x + 40, "y": self.y + 40, "width": 20, "height": 20, "health": 150}
        ]

def create_boss(boss_type, x, y):
    """Factory function to create boss enemies"""
    boss_classes = {
        "hive_tyrant": HiveTyrantBoss,
        "swarmlord": SwarmlordBoss
    }
    
    boss_class = boss_classes.get(boss_type.lower())
    if boss_class:
        return boss_class(x, y)
    return None 