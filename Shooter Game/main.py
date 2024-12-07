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
RED = (255, 0, 0)
screen.fill(BG)

# Game FPS for Game Loop
clock = pygame.time.Clock()
FPS = 60

# Initalise Example Players & Characters
player = classes.Entity(250, 250, 3, 2, "player")
#enemy = classes.Entity(300, 400, 0.05, 2, "enemy")
running = True

while running:

    clock.tick(FPS)

    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

    player.draw()
    #enemy.draw()

    # Update the player actions and adjust animation appropriately
    if player.alive:
        if player.in_air:
            player.update_actions(2) # jump
        elif moving_left or moving_right:
            player.update_actions(1)
        else:
            player.update_actions(0)

        player.move(moving_left, moving_right)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                running = False
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
	
    

    pygame.display.update()

pygame.quit()