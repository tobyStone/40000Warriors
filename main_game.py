import pygame
import sys
import os
import math
import random
from cutscene_player import play_intro_cutscene

# Import game modules
# One approach is to manually traverse to the proper repo root
project_root = os.path.join(os.path.dirname(__file__), "..", "40000Warriors")
assets_path = os.path.join(project_root, "assets")
sys.path.append(assets_path)

from tyranid_sprites import create_tyranid
from interior_3d import Interior3D
from scout_marine import ScoutMarine
from ui_system import UISystem
from npc_system import create_npc, DialogueSystem
from room_system import Room, RoomManager, create_transition
from boss_system import create_boss
from pickup_system import PickupManager

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)

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
        # Return a fallback colored surface (magenta for missing textures)
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        surf.fill((255, 0, 255))
        return surf

class Game:
    def __init__(self):
        # Load assets with proper path handling
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.is_fullscreen = False
        
        # Game state
        self.game_over = False
        self.game_won = False
        self.game_paused = False
        
        # Player
        self.player = ScoutMarine(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # UI
        self.ui = UISystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Dialogue system
        self.dialogue = DialogueSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Room system
        self.room_manager = RoomManager()
        self.setup_rooms()
        
        # Enemy system
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = 5000  # 5 seconds
        
        # Boss system
        self.current_boss = None
        self.boss_active = False
        self.boss_room = None
        
        # Pickup system
        self.pickup_manager = PickupManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # NPC system
        self.npcs = []
        self.setup_npcs()
        
        # Game timer
        self.game_timer = 0
        self.last_update_time = pygame.time.get_ticks()
        
        # Set initial objective
        self.ui.set_objective("Explore the gothic hall and eliminate Tyranid threats")
        
        # Ammo system
        self.ammo = 30
        self.max_ammo = 30
        self.ui.update_ammo(self.ammo, self.max_ammo)
        
        # Kill counter
        self.kills = 0

    def setup_npcs(self):
        """Set up NPCs in the game"""
        # Add some NPCs to different rooms
        self.npcs.append(create_npc("soldier", 100, 100, "Sergeant Tarkus"))
        self.npcs.append(create_npc("tech_priest", 200, 200, "Magos Vex"))
        self.npcs.append(create_npc("inquisitor", 300, 300, "Inquisitor Kryptman"))
    
    def setup_rooms(self):
        """Set up rooms in the game"""
        # Create rooms
        main_hall = Room("Main Hall", "gothic_hall.png", 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        armory = Room("Armory", "armory.png", 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        chapel = Room("Chapel", "chapel.png", 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        boss_arena = Room("Boss Arena", "boss_arena.png", 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Add rooms to manager
        self.room_manager.add_room(main_hall)
        self.room_manager.add_room(armory)
        self.room_manager.add_room(chapel)
        self.room_manager.add_room(boss_arena)
        
        # Create transitions
        main_hall.add_exit(create_transition("armory", 700, 300, 100, 100))
        main_hall.add_exit(create_transition("chapel", 300, 500, 100, 100))
        armory.add_exit(create_transition("main_hall", 50, 300, 100, 100))
        chapel.add_exit(create_transition("main_hall", 300, 50, 100, 100))
        
        # Set boss room
        self.boss_room = boss_arena
        main_hall.add_exit(create_transition("boss_arena", 400, 50, 100, 100))
        
        # Set starting room
        self.room_manager.set_current_room("Main Hall")
    
    def spawn_enemy(self):
        """Spawn a new enemy"""
        if len(self.enemies) < 10:  # Limit number of enemies
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            
            # Randomly choose enemy type
            enemy_types = ["genestealer", "warrior", "gaunt", "lictor", "carnifex", "zoanthrope",
                          "hive_tyrant", "harpy", "mawloc"]
            enemy_type = random.choice(enemy_types)
            
            enemy = create_tyranid(enemy_type, x, y)
            if enemy:
                self.enemies.append(enemy)
    
    def spawn_boss(self, boss_type):
        """Spawn a boss enemy"""
        if self.current_boss is None:
            x = SCREEN_WIDTH // 2
            y = SCREEN_HEIGHT // 2
            self.current_boss = create_boss(boss_type, x, y)
            self.boss_active = True
            self.room_manager.set_current_room("Boss Arena")
    
    def check_bullet_collisions(self):
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        hit_enemies = self.player.check_bullet_collisions(current_room.enemies)
        for enemy in hit_enemies:
            if enemy in current_room.enemies:
                current_room.enemies.remove(enemy)
                self.kills += 1
                self.ui.increment_kills()
                self.ui.add_message(f"Enemy eliminated! ({self.kills} kills)", (0, 255, 0))
    
    def check_melee_attack(self):
        if not self.player.is_attacking:
            return
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        damaged_enemies = self.player.check_enemy_collision(current_room.enemies)
        for enemy in damaged_enemies:
            if enemy in current_room.enemies:
                current_room.enemies.remove(enemy)
                self.kills += 1
                self.ui.increment_kills()
                self.ui.add_message(f"Enemy slain in melee! ({self.kills} kills)", (0, 255, 0))
    
    def check_enemy_collisions(self):
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        for enemy in current_room.enemies:
            if (self.player.x < enemy.x + enemy.width and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.height and
                self.player.y + self.player.height > enemy.y):
                if self.player.take_damage(enemy.damage * 0.1):
                    self.game_over = True
                self.ui.update_player_health(self.player.health, self.player.max_health)
    
    def check_npc_interactions(self):
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        for npc in current_room.npcs:
            dx = (self.player.x + self.player.width // 2) - (npc.x + npc.width // 2)
            dy = (self.player.y + self.player.height // 2) - (npc.y + npc.height // 2)
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 80:  # Interaction range
                font = pygame.font.SysFont('Arial', 16)
                text = font.render("Press E to interact", True, WHITE)
                screen.blit(text, (npc.x, npc.y - 20))
    
    def interact_with_npc(self):
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        for npc in current_room.npcs:
            dx = (self.player.x + self.player.width // 2) - (npc.x + npc.width // 2)
            dy = (self.player.y + self.player.height // 2) - (npc.y + npc.height // 2)
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 80:
                dialogue_data = npc.interact()
                self.dialogue.start_dialogue(dialogue_data)
                break
    
    def check_room_transitions(self):
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        for transition in current_room.transitions:
            if transition.can_activate(self.player.x, self.player.y, self.player.width, self.player.height):
                font = pygame.font.SysFont('Arial', 16)
                text = font.render("Press SPACE to enter", True, WHITE)
                screen.blit(text, (transition.x, transition.y - 20))
    
    def activate_room_transition(self):
        current_room = self.room_manager.get_current_room()
        if not current_room:
            return
        for transition in current_room.transitions:
            if transition.can_activate(self.player.x, self.player.y, self.player.width, self.player.height):
                target_room = transition.activate()
                if target_room:
                    self.room_manager.transition_to_room(target_room, "fade")
                    
                    # Place player on opposite side of the new room
                    if transition.x <= 0:
                        self.player.x = SCREEN_WIDTH - self.player.width - 60
                    elif transition.x >= SCREEN_WIDTH - transition.width:
                        self.player.x = 60
                    if transition.y <= 0:
                        self.player.y = SCREEN_HEIGHT - self.player.height - 60
                    elif transition.y >= SCREEN_HEIGHT - transition.height:
                        self.player.y = 60
                    
                    self.ui.add_message(f"Entered {target_room.replace('_', ' ').title()}")
                    
                    new_room = self.room_manager.get_current_room()
                    if new_room and not new_room.is_visited:
                        new_room.is_visited = True
                        if target_room == "side_chamber":
                            self.ui.set_objective("Clear the side chamber of Tyranid infestation")
                        elif target_room == "armory":
                            self.ui.set_objective("Speak with the Commissar in the armory")
                    
                    break
    
    def shoot(self):
        if self.ammo <= 0:
            self.ui.add_message("Out of ammo!", RED)
            return False
        if self.player.shoot():
            self.ammo -= 1
            self.ui.update_ammo(self.ammo, self.max_ammo)
            return True
        return False
    
    def reload(self):
        if self.ammo < self.max_ammo:
            self.ammo = self.max_ammo
            self.ui.update_ammo(self.ammo, self.max_ammo)
            self.ui.add_message("Reloaded!")
            return True
        return False
    
    def toggle_fullscreen(self):
        """Toggle between windowed and fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            # Update UI system with new screen dimensions
            self.ui = UISystem(self.screen.get_width(), self.screen.get_height())
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.ui = UISystem(SCREEN_WIDTH, SCREEN_HEIGHT)

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and (self.game_over or self.game_won):
                    self.restart()
                if event.key == pygame.K_p:
                    self.game_paused = not self.game_paused
                if not self.game_over and not self.game_paused and not self.game_won:
                    if event.key == pygame.K_e:
                        self.interact_with_npc()
                    if event.key == pygame.K_SPACE:
                        self.activate_room_transition()
                    if event.key == pygame.K_f:
                        self.player.melee_attack()
                    if event.key == pygame.K_r:
                        self.reload()
                if self.dialogue.active:
                    if event.key == pygame.K_e:
                        self.dialogue.end_dialogue()
                    elif event.key == pygame.K_UP:
                        self.dialogue.select_prev_response()
                    elif event.key == pygame.K_DOWN:
                        self.dialogue.select_next_response()
                    elif event.key == pygame.K_SPACE:
                        self.dialogue.skip_animation()
        return True

    def update(self):
        """Update game state"""
        if not self.handle_events():
            return False
        
        if self.game_over or self.game_paused:
            return True
        
        # Update game timer
        current_time = pygame.time.get_ticks()
        self.game_timer += current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update player
        self.player.update()
        
        # Update current room
        self.room_manager.update_current_room()
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self.ui.increment_kills()
        
        # Update boss
        if self.current_boss:
            self.current_boss.update()
            if self.current_boss.health <= 0:
                self.current_boss = None
                self.boss_active = False
                self.game_won = True
        
        # Spawn new enemies
        if current_time - self.spawn_timer > self.spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = current_time
        
        # Update pickups
        self.pickup_manager.update()
        
        # Update NPCs
        for npc in self.npcs:
            npc.update(self.player.x, self.player.y)
        
        # Check collisions
        self.check_bullet_collisions()
        self.check_melee_attack()
        self.check_enemy_collisions()
        self.check_npc_interactions()
        self.check_room_transitions()
        self.pickup_manager.check_collisions(self.player)
        
        # Update UI
        self.ui.update_player_health(self.player.health, self.player.max_health)
        self.ui.update_player_armor(self.player.armor, self.player.max_armor)
        self.ui.update_ammo(self.player.current_ammo, self.player.max_ammo)
        
        return True
    
    def draw(self):
        """Draw the game"""
        # Draw current room
        self.room_manager.draw_current_room(self.screen)
        
        # Draw pickups
        self.pickup_manager.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw boss
        if self.current_boss:
            self.current_boss.draw(self.screen)
        
        # Draw NPCs
        for npc in self.npcs:
            npc.draw(self.screen)
        
        # Draw UI
        self.ui.draw(self.screen)
        
        # Draw dialogue
        if self.dialogue.active:
            self.dialogue.draw(self.screen)
        
        # Draw game over or victory screen
        if self.game_over:
            self.draw_game_over()
        elif self.game_won:
            self.draw_victory()
        
        # Draw pause menu
        if self.game_paused:
            self.draw_pause_menu()
    
    def draw_pause_menu(self):
        """Draw the pause menu"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        font = pygame.font.SysFont('Arial', 48)
        text = font.render("PAUSED", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(text, text_rect)
        
        # Draw resume instructions
        font = pygame.font.SysFont('Arial', 24)
        text = font.render("Press P to resume", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(text, text_rect)
    
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont('Arial', 60)
        text = font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
        
        font = pygame.font.SysFont('Arial', 30)
        text = font.render("Press R to restart", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        screen.blit(text, text_rect)
        
        font = pygame.font.SysFont('Arial', 24)
        text = font.render(f"Tyranids eliminated: {self.kills}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(text, text_rect)
    
    def draw_victory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 50))
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont('Arial', 60)
        text = font.render("VICTORY", True, (255, 215, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text, text_rect)
        
        font = pygame.font.SysFont('Arial', 30)
        text = font.render("The Emperor Protects", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
        
        font = pygame.font.SysFont('Arial', 24)
        text = font.render(f"Tyranids eliminated: {self.kills}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(text, text_rect)
        
        font = pygame.font.SysFont('Arial', 24)
        text = font.render("Press R to play again or ESC to quit", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(text, text_rect)
    
    def restart(self):
        self.__init__()

def main():

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    cutscene_path = os.path.join(project_root, "assets", "cut_scenes", "intro.mp4")


    
    # Check if the cutscene file exists
    if os.path.exists(cutscene_path):
        play_intro_cutscene(cutscene_path)
    else:
        print(f"Warning: Cutscene file not found at {cutscene_path}")

    game = Game()
    running = True

    
    while running:
        running = game.update()
        screen.fill(BLACK)
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

