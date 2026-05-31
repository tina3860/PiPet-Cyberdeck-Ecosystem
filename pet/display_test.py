import pygame
import sys
import os

# THIS IS THE KEY LINE - set display environment
os.environ["SDL_VIDEODRIVER"] = "fbcon"
os.environ["SDL_FBDEV"] = "/dev/fb1"

# Initialize pygame
pygame.init()

# Whisplay HAT screen size
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 280

# Create display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PIPET Status Page Test")
clock = pygame.time.Clock()

# Load status page
try:
    status_page = pygame.image.load('assets/ui/Status_page.png')
    print("✓ Status page loaded!")
except:
    print("✗ Could not load status page")
    sys.exit()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Display the status page
    screen.blit(status_page, (0, 0))

    # Update display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
print("Test complete!")