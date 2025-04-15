import os
import sys
import pygame
import cv2
from cutscene_player import play_intro_cutscene

def create_placeholder_cutscene():
    """Create a placeholder cutscene text file if no video is available"""
    cutscene_dir = os.path.join("assets", "cut_scenes")
    os.makedirs(cutscene_dir, exist_ok=True)
    
    placeholder_path = os.path.join(cutscene_dir, "intro_text.txt")
    with open(placeholder_path, "w") as f:
        f.write("In the grim darkness of the far future, there is only war.\n\n")
        f.write("A Space Marine Scout has been deployed to investigate\n")
        f.write("a Tyranid infestation in an ancient gothic cathedral.\n\n")
        f.write("Purge the xenos threat in the name of the Emperor!")
    
    return placeholder_path

def show_text_cutscene(text_path):
    """Display a text-based cutscene"""
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("40000 Warriors - Intro")
    
    # Load text
    try:
        with open(text_path, "r") as f:
            story_text = f.readlines()
    except:
        story_text = [
            "In the grim darkness of the far future, there is only war.",
            "",
            "A Space Marine Scout has been deployed to investigate",
            "a Tyranid infestation in an ancient gothic cathedral.",
            "",
            "Purge the xenos threat in the name of the Emperor!"
        ]
    
    # Setup fonts
    title_font = pygame.font.SysFont('Arial', 48)
    text_font = pygame.font.SysFont('Arial', 24)
    
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GOLD = (255, 215, 0)
    RED = (255, 0, 0)
    
    # Create background with fade-in effect
    for alpha in range(0, 256, 5):
        screen.fill(BLACK)
        
        # Draw title with fade-in
        title = title_font.render("WARHAMMER 40,000", True, GOLD)
        title.set_alpha(alpha)
        screen.blit(title, (screen_width//2 - title.get_width()//2, 100))
        
        subtitle = title_font.render("WARRIORS", True, RED)
        subtitle.set_alpha(alpha)
        screen.blit(subtitle, (screen_width//2 - subtitle.get_width()//2, 160))
        
        pygame.display.flip()
        pygame.time.delay(30)
    
    # Display story text with typing effect
    y_pos = 250
    for line in story_text:
        if line.strip():  # Skip empty lines for display but add spacing
            rendered_text = text_font.render(line.strip(), True, WHITE)
            
            # Typing effect
            for i in range(len(line.strip()) + 1):
                screen.fill(BLACK)
                
                # Redraw title and subtitle
                screen.blit(title, (screen_width//2 - title.get_width()//2, 100))
                screen.blit(subtitle, (screen_width//2 - subtitle.get_width()//2, 160))
                
                # Draw previously completed lines
                temp_y = 250
                for prev_line in story_text:
                    if temp_y < y_pos and prev_line.strip():
                        prev_text = text_font.render(prev_line.strip(), True, WHITE)
                        screen.blit(prev_text, (screen_width//2 - prev_text.get_width()//2, temp_y))
                    temp_y += 40 if prev_line.strip() else 20
                
                # Draw current line with typing effect
                current_text = text_font.render(line.strip()[:i], True, WHITE)
                screen.blit(current_text, (screen_width//2 - rendered_text.get_width()//2, y_pos))
                
                # Draw press key message
                if i == len(line.strip()):
                    press_key = text_font.render("Press any key to continue", True, (150, 150, 150))
                    screen.blit(press_key, (screen_width//2 - press_key.get_width()//2, 500))
                
                pygame.display.flip()
                
                # Check for key press to skip
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        i = len(line.strip())  # Skip to end of line
                
                pygame.time.delay(30)
        
        y_pos += 40 if line.strip() else 20
    
    # Wait for key press to continue
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                waiting = False
    
    # Fade out
    for alpha in range(255, -1, -5):
        fade = pygame.Surface((screen_width, screen_height))
        fade.fill(BLACK)
        fade.set_alpha(255 - alpha)
        screen.blit(fade, (0, 0))
        pygame.display.flip()
        pygame.time.delay(30)

def main():
    """
    Main entry point for the 40000 Warriors game.
    Plays the intro cutscene and then launches the main game.
    """
    # Initialize pygame
    pygame.init()
    
    # Set up display for initial loading screen
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("40000 Warriors - Loading...")
    
    # Display loading screen
    font = pygame.font.SysFont('Arial', 32)
    loading_text = font.render("Loading 40000 Warriors...", True, (255, 255, 255))
    screen.fill((0, 0, 0))
    screen.blit(loading_text, (screen_width//2 - loading_text.get_width()//2, 
                              screen_height//2 - loading_text.get_height()//2))
    pygame.display.flip()
    
    # Check if cutscene file exists
    cutscene_path = os.path.join("assets", "cut_scenes", "intro.mp4")
    if not os.path.exists(cutscene_path):
        # Try to find any video file in the cutscenes directory
        cutscene_dir = os.path.join("assets", "cut_scenes")
        if os.path.exists(cutscene_dir):
            for file in os.listdir(cutscene_dir):
                if file.endswith(('.mp4', '.avi', '.mov')):
                    cutscene_path = os.path.join(cutscene_dir, file)
                    break
    
    # Check if OpenCV is available
    try:
        import cv2
        cv2_available = True
    except ImportError:
        cv2_available = False
        print("OpenCV (cv2) not available. Will use text-based cutscene.")
    
    # Play cutscene or show text intro
    if os.path.exists(cutscene_path) and cv2_available:
        try:
            # Play the intro cutscene
            play_intro_cutscene(cutscene_path)
        except Exception as e:
            print(f"Error playing cutscene: {e}")
            # Fallback to text cutscene
            text_path = create_placeholder_cutscene()
            show_text_cutscene(text_path)
    else:
        # Create and show text-based cutscene
        text_path = create_placeholder_cutscene()
        show_text_cutscene(text_path)
    
    # Import and start the main game
    try:
        import main_game as main
        # The main module has its own game loop
    except ImportError as e:
        print(f"Error importing main game module: {e}")
        error_text = font.render("Error: Could not load main game module", True, (255, 0, 0))
        screen.fill((0, 0, 0))
        screen.blit(error_text, (screen_width//2 - error_text.get_width()//2, 
                                screen_height//2 - error_text.get_height()//2))
        pygame.display.flip()
        
        # Wait for a few seconds before exiting
        pygame.time.wait(5000)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
