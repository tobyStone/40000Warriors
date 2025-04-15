import pygame
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main game module
try:
    from main_game import main
    print("Successfully imported main game module")
except ImportError as e:
    print(f"Error importing main game module: {e}")
    sys.exit(1)

if __name__ == "__main__":
    # Initialize pygame
    pygame.init()
    
    # Run the main game function
    try:
        main()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)



