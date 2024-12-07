import pygame
import classes
pygame.init()

# Initialise screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Random Shooter Game")

# Any random variables go here
running = True
moving_left = False
moving_right = False

# Initialise background
BG = (144, 201, 120)
screen.fill(BG)

# Game FPS for Game Loop
clock = pygame.time.Clock()
FPS = 60

# Initialise player boilerplate code
x = 250
y = 250
scale = 0.125/2

player = classes.Entity(x, y, scale, 2, "player")
running = True
while running:

    clock.tick(FPS)

    screen.fill(BG)

    player.draw()
    player.move(moving_left, moving_right)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_ESCAPE:
                running = False
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
	
    

    pygame.display.update()

pygame.quit()