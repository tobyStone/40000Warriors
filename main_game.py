import pygame
import sys
import os
import math
import random

# Import game modules
sys.path.append(os.path.join(os.path.dirname(__file__), "assets"))
from tyranid_sprites import create_tyranid
from interior_3d import Interior3D
from scout_marine import ScoutMarine
from ui_system import UISystem
from npc_system import create_npc, DialogueSystem
from room_system import Room, RoomManager, create_transition

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("40000 Warriors - Space Marine Scout")

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Asset paths
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# Load images
def load_image(filename):
    try:
        return pygame.image.load(os.path.join(ASSETS_DIR, filename)).convert_alpha()
    except pygame.error:
        print(f"Unable to load image: {filename}")
        # Return a colored surface as fallback
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        surf.fill((255, 0, 255))  # Magenta for missing textures
        return surf

class Game:
    def __init__(self):
        # Load assets
        self.hall_bg = load_image("gothic_hall.png")
        
        # Create player
        self.player = ScoutMarine(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Create UI system
        self.ui = UISystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Create dialogue system
        self.dialogue = DialogueSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Create room manager
        self.room_manager = RoomManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Set up rooms
        self.setup_rooms()
        
        # Game state
        self.game_over = False
        self.game_paused = False
        self.game_won = False
        
        # Enemy spawn timer
        self.last_enemy_spawn = 0
        self.enemy_spawn_cooldown = 5000  # milliseconds
        
        # Set initial objectives
        self.ui.set_objective("Explore the gothic hall and eliminate Tyranid threats")
        
        # Ammo system
        self.ammo = 30
        self.max_ammo = 30
        self.ui.update_ammo(self.ammo, self.max_ammo)
        
        # Kill counter
        self.kills = 0
    
    def setup_rooms(self):
        # Main hall room
        main_hall = Room("main_hall", self.hall_bg)
        
        # Create 3D interior for main hall
        interior = Interior3D(os.path.join(ASSETS_DIR, "gothic_hall.png"), SCREEN_WIDTH, SCREEN_HEIGHT)
        interior.add_graffiti("The Emperor Protects", (200, 100), (255, 215, 0))
        interior.add_graffiti("Beware the Xenos", (500, 400), (255, 0, 0))
        interior.add_light_source((300, 200), (255, 200, 100), 150)
        interior.add_light_source((500, 300), (200, 200, 255), 120)
        main_hall.set_interior_3d(interior)
        
        # Add NPCs to main hall
        soldier_npc = create_npc("soldier", 100, 300, "Sergeant Tarkus")
        tech_priest = create_npc("tech_priest", 700, 300, "Magos Drakk")
        main_hall.add_npc(soldier_npc)
        main_hall.add_npc(tech_priest)
        
        # Add room transitions
        side_chamber_door = create_transition("door", 750, 250, 50, 100, "side_chamber")
        armory_door = create_transition("door", 0, 250, 50, 100, "armory")
        main_hall.add_transition(side_chamber_door)
        main_hall.add_transition(armory_door)
        
        # Add initial enemies
        genestealer = create_tyranid("genestealer", 600, 100)
        warrior = create_tyranid("warrior", 200, 500)
        main_hall.add_enemy(genestealer)
        main_hall.add_enemy(warrior)
        
        # Add room to game rooms
        self.room_manager.add_room("main_hall", main_hall)
        
        # Side chamber room
        side_chamber = Room("side_chamber")
        side_interior = Interior3D(os.path.join(ASSETS_DIR, "gothic_hall.png"), SCREEN_WIDTH, SCREEN_HEIGHT)
        side_interior.add_graffiti("Sanctum Imperialis", (300, 200), (0, 200, 200))
        side_interior.add_light_source((400, 250), (100, 100, 255), 200)
        side_chamber.set_interior_3d(side_interior)
        
        side_chamber.add_transition(create_transition("door", 0, 250, 50, 100, "main_hall"))
        side_chamber.add_enemy(create_tyranid("carnifex", 400, 300))
        side_chamber.add_enemy(create_tyranid("gaunt", 300, 200))
        side_chamber.add_enemy(create_tyranid("gaunt", 500, 200))
        
        self.room_manager.add_room("side_chamber", side_chamber)
        
        # Armory room
        armory = Room("armory")
        armory_interior = Interior3D(os.path.join(ASSETS_DIR, "gothic_hall.png"), SCREEN_WIDTH, SCREEN_HEIGHT)
        armory_interior.add_graffiti("Imperial Armory", (300, 200), (200, 200, 200))
        armory_interior.add_light_source((400, 300), (255, 150, 50), 180)
        armory.set_interior_3d(armory_interior)
        
        armory.add_transition(create_transition("door", 750, 250, 50, 100, "main_hall"))
        armory.add_npc(create_npc("commissar", 400, 300, "Commissar Yarrick"))
        
        self.room_manager.add_room("armory", armory)
    
    def spawn_enemy(self):
        """Spawn a new enemy in the current room"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_enemy_spawn > self.enemy_spawn_cooldown:
            self.last_enemy_spawn = current_time
            
            # Get current room
            current_room = self.room_manager.get_current_room()
            if not current_room or len(current_room.enemies) >= 5:
                return  # Don't spawn if room is full
            
            # Random position at the edge of the screen
            side = random.randint(0, 3)
            if side == 0:  # Top
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = 0
            elif side == 1:  # Right
                x = SCREEN_WIDTH
                y = random.randint(50, SCREEN_HEIGHT - 50)
            elif side == 2:  # Bottom
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = SCREEN_HEIGHT
            else:  # Left
                x = 0
                y = random.randint(50, SCREEN_HEIGHT - 50)
            
            # Random enemy type
            enemy_types = ["genestealer", "warrior", "gaunt", "lictor", "zoanthrope"]
            weights = [0.3, 0.2, 0.3, 0.1, 0.1]  # Probability weights
            enemy_type = random.choices(enemy_types, weights=weights, k=1)[0]
            
            # Add enemy to current room
            current_room.add_enemy(create_tyranid(enemy_type, x, y))
    
    def check_bullet_collisions(self):
        """Check for collisions between bullets and enemies"""
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        
        hit_enemies = self.player.check_bullet_collisions(current_room.enemies)
        
        # Remove dead enemies
        for enemy in hit_enemies:
            if enemy in current_room.enemies:
                current_room.enemies.remove(enemy)
                self.kills += 1
                self.ui.increment_kills()
                
                # Add message
                self.ui.add_message(f"Enemy eliminated! ({self.kills} kills)", (0, 255, 0))
    
    def check_melee_attack(self):
        """Check for melee attacks hitting enemies"""
        if not self.player.is_attacking:
            return
            
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        
        damaged_enemies = self.player.check_enemy_collision(current_room.enemies)
        
        # Remove dead enemies
        for enemy in damaged_enemies:
            if enemy in current_room.enemies:
                current_room.enemies.remove(enemy)
                self.kills += 1
                self.ui.increment_kills()
                
                # Add message
                self.ui.add_message(f"Enemy slain in melee! ({self.kills} kills)", (0, 255, 0))
    
    def check_enemy_collisions(self):
        """Check if enemies are colliding with player"""
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        
        # Check if enemies are colliding with player
        for enemy in current_room.enemies:
            # Simple collision check
            if (self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                
                # Player takes damage
                if self.player.take_damage(enemy.damage * 0.1):  # Reduced for gameplay balance
                    self.game_over = True
                
                # Update UI
                self.ui.update_player_health(self.player.health, self.player.max_health)
    
    def check_npc_interactions(self):
        """Check for NPC interactions"""
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        
        # Check if player is near any NPCs
        for npc in current_room.npcs:
            if npc.can_interact(self.player.x + self.player.width//2, self.player.y + self.player.height//2):
                # Show interaction prompt
                font = pygame.font.SysFont('Arial', 16)
                text = font.render("Press E to interact", True, WHITE)
                screen.blit(text, (npc.x, npc.y - 20))
    
    def interact_with_npc(self):
        """Interact with nearby NPCs"""
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        
        # Check if player is near any NPCs
        for npc in current_room.npcs:
            if npc.can_interact(self.player.x + self.player.width//2, self.player.y + self.player.height//2):
                # Get dialogue
                dialogue_data = npc.interact()
                self.dialogue.start_dialogue(dialogue_data)
                break
    
    def check_room_transitions(self):
        """Check for room transitions"""
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        
        # Check if player is colliding with any room transitions
        for transition in current_room.transitions:
            if transition.can_activate(self.player.x, self.player.y, self.player.width, self.player.height):
                # Show transition prompt
                font = pygame.font.SysFont('Arial', 16)
                text = font.render("Press SPACE to enter", True, WHITE)
                screen.blit(text, (transition.x, transition.y - 20))
    
    def activate_room_transition(self):
        """Activate a room transition"""
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        
        # Check if player is colliding with any room transitions
        for transition in current_room.transitions:
            if transition.can_activate(self.player.x, self.player.y, self.player.width, self.player.height):
                target_room = transition.activate()
                if target_room:
                    # Transition to new room
                    self.room_manager.transition_to_room(target_room, "fade")
                    
                    # Place player on the opposite side of the new room
                    if transition.x <= 0:
                        self.player.x = SCREEN_WIDTH - self.player.width - 60
                    elif transition.x >= SCREEN_WIDTH - transition.width:
                        self.player.x = 60
                    if transition.y <= 0:
                        self.player.y = SCREEN_HEIGHT - self.player.height - 60
                    elif transition.y >= SCREEN_HEIGHT - transition.height:
                        self.player.y = 60
                    
                    # Add message
                    self.ui.add_message(f"Entered {target_room.replace('_', ' ').title()}")
                    
                    # Mark room as visited
                    new_room = self.room_manager.get_current_room()
                    if new_room and not new_room.is_visited:
                        new_room.is_visited = True
                        
                        # Set new objective if entering a new room
                        if target_room == "side_chamber":
                            self.ui.set_objective("Clear the side chamber of Tyranid infestation")
                        elif target_room == "armory":
                            self.ui.set_objective("Speak with the Commissar in the armory")
                    
                    break
    
    def shoot(self):
        """Player shoots a bullet"""
        if self.ammo <= 0:
            self.ui.add_message("Out of ammo!", RED)
            return False
        
        if self.player.shoot():
            self.ammo -= 1
            self.ui.update_ammo(self.ammo, self.max_ammo)
            return True
        
        return False
    
    def reload(self):
        """Reload player's weapon"""
        if self.ammo < self.max_ammo:
            self.ammo = self.max_ammo
            self.ui.update_ammo(self.ammo, self.max_ammo)
            self.ui.add_message("Reloaded!")
            return True
        
        return False
    
    def update(self):
        """Update game state"""
        if self.game_over or self.game_paused:
            return
        
        # Update player
        self.player.update()
        
        # Update room manager
        self.room_manager.update()
        
        # Update UI
        self.ui.update()
        
        # Update dialogue
        self.dialogue.update()
        
        # Spawn enemies
        self.spawn_enemy()
        
        # Check collisions
        self.check_bullet_collisions()
        self.check_melee_attack()
        self.check_enemy_collisions()
        
        # Update UI health display
        self.ui.update_player_health(self.player.health, self.player.max_health)
        
        # Update enemy health display if player is targeting an enemy
        current_room = self.room_manager.get_current_room()
        if current_room and current_room.enemies:
            # Find closest enemy for health display
            closest_enemy = None
            min_distance = float('inf')
            
            for enemy in current_room.enemies:
                dx = enemy.x - self.player.x
                dy = enemy.y - self.player.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_enemy = enemy
            
            if closest_enemy and min_distance < 200:  # Only show health for nearby enemies
                self.ui.update_enemy_health(closest_enemy.health, closest_enemy.max_health)
            else:
                self.ui.update_enemy_health(0, 100)  # Hide enemy health bar
        
        # Check for victory condition
        if self.kills >= 20:
            self.game_won = True
            self.ui.add_message("Victory! The Tyranid threat has been contained.", (0, 255, 0))
            self.ui.complete_objective()
    
    def draw(self):
        """Draw the game"""
        # Draw current room
        self.room_manager.draw(screen)
        
        # Draw player
        self.player.draw(screen)
        
        # Draw UI
        self.ui.draw(screen)
        
        # Draw dialogue
        self.dialogue.draw(screen)
        
        # Draw NPC interaction prompts
        self.check_npc_interactions()
        
        # Draw room transition prompts
        self.check_room_transitions()
        
        # Draw game over screen if needed
        if self.game_over:
            self.draw_game_over()
        
        # Draw victory screen if needed
        if self.game_won:
            self.draw_victory()
    
    def draw_game_over(self):
        """Draw the game over screen"""
        # Darken screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw game over text
        font = pygame.font.SysFont('Arial', 60)
        text = font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text, text_rect)
        
        # Draw restart instruction
        font = pygame.font.SysFont('Arial', 30)
        text = font.render("Press R to restart", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        screen.blit(text, text_rect)
        
        # Draw kill count
        font = pygame.font.SysFont('Arial', 24)
        text = font.render(f"Tyranids eliminated: {self.kills}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        screen.blit(text, text_rect)
    
    def draw_victory(self):
        """Draw the victory screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 50))  # Dark blue
        screen.blit(overlay, (0, 0))
        
        # Draw victory text
        font = pygame.font.SysFont('Arial', 60)
        text = font.render("VICTORY", True, (255, 215, 0))  # Gold
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(text, text_rect)
        
        # Draw subtitle
        font = pygame.font.SysFont('Arial', 30)
        text = font.render("The Emperor Protects", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text, text_rect)
        
        # Draw kill count
        font = pygame.font.SysFont('Arial', 24)
        text = font.render(f"Tyranids eliminated: {self.kills}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(text, text_rect)
        
        # Draw continue instruction
        font = pygame.font.SysFont('Arial', 24)
        text = font.render("Press R to play again or ESC to quit", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))
        screen.blit(text, text_rect)
    
    def restart(self):
        """Restart the game"""
        self.__init__()

# Main game loop
def main():
    game = Game()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                if event.key == pygame.K_r and (game.game_over or game.game_won):
                    game.restart()
                
                if event.key == pygame.K_p:
                    game.game_paused = not game.game_paused
                
                if not game.game_over and not game.game_paused and not game.game_won:
                    if event.key == pygame.K_e:
                        game.interact_with_npc()
                    
                    if event.key == pygame.K_SPACE:
                        game.activate_room_transition()
                    
                    if event.key == pygame.K_f:
                        game.player.melee_attack()
                    
                    if event.key == pygame.K_r:
                        game.reload()
                
                # Handle dialogue navigation
                if game.dialogue.active:
                    if event.key == pygame.K_e:
                        game.dialogue.end_dialogue()
                    elif event.key == pygame.K_UP:
                        game.dialogue.select_prev_response()
                    elif event.key == pygame.K_DOWN:
                        game.dialogue.select_next_response()
                    elif event.key == pygame.K_SPACE:
                        game.dialogue.skip_animation()
        
        # Handle continuous key presses for movement and shooting
        if not game.game_over and not game.game_paused and not game.game_won and not game.dialogue.active:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -game.player.velocity
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = game.player.velocity
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -game.player.velocity
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = game.player.velocity
            
            game.player.move(dx, dy)
            
            # Continuous shooting with cooldown
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL] or pygame.mouse.get_pressed()[0]:
                game.shoot()
        
        # Update game state
        game.update()
        
        # Draw everything
        screen.fill(BLACK)  # Clear screen
        game.draw()
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
