import cv2
import pygame
import sys

def play_intro_cutscene(video_path):
    # Init pygame
    pygame.init()

    # Load the video
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print("Error: Could not open video.")
        return

    # Get video details
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Intro Cutscene")

    clock = pygame.time.Clock()

    while True:
        ret, frame = video.read()
        if not ret:
            break  # End of video

        # Convert BGR (OpenCV) to RGB (Pygame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.blit(frame, (0, 0))
        pygame.display.update()
        clock.tick(fps)

    video.release()

# Expose play_intro_cutscene if you want to import them from elsewhere
__all__ = ["play_intro_cutscene"]

