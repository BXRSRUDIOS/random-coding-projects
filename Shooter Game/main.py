import pygame
import classes
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Random Shooter Game")

running = True


# Initialise player boilerplate code
x = 250
y = 250
scale = 0.125/2

player = classes.Entity(x, y, scale)

while running:

    player.draw()

    for event in pygame.event.get(): # quit the game
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

pygame.quit()