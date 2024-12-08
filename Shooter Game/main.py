import pygame
import os
pygame.init()

# Initialise screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Random Shooter Game")

# Any random action variables go here
running = True
moving_left = False
moving_right = False
shoot = False

# Initialise background
BG = (0, 0, 0)
RED = (255, 0, 0)
screen.fill(BG)

# Game FPS for Game Loop
clock = pygame.time.Clock()
FPS = 60

# Images
bullet_img = pygame.image.load("Shooter Game/Other Assets/bullet.png")

# Create Sprite Groups
bullet_group = pygame.sprite.Group()

# Initalise Other variables
running = True
GRAVITY = 0.75

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, velocity, ammo, char_type):
        # Temporary Placeholder image for all entities
        super().__init__()
        # Main Attributes
        self.alive = True
        self.velocity = velocity
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.jump = False
        self.vel_y = 0
        self.in_air = True
        self.flip = False
        self.char_type = char_type
        self.animation_list = []
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        
        # Loading Images - All Images for Players
        animation_types = ["Idle", "Run", "Jump", "Shoot Idle", "Shoot Move", "Death"]
        for animation in animation_types:
            # Reset temp list of imgs
            temp_list = []
            num_frames = len(os.listdir(f"Shooter Game/{self.char_type}/{animation}"))
            for i in range(1, num_frames+1):
                img = pygame.image.load(f"Shooter Game/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_width() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        # Get First Frame & Rect
        # Action 0 = Idle, Action 1 = Run, Action 2 = Jump etc
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.velocity
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.velocity
            self.flip = False
            self.direction = 1

        if self.jump == True and self.in_air == False:
            self.vel_y = -15
            self.jump = False
            self.in_air = True

        # Apply Gravity
        self.vel_y += GRAVITY
        if self.vel_y > 14:
            self.vel_y = 14
        dy += self.vel_y

        # Temp check for collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        self.rect.x += dx  
        self.rect.y += dy
    
    def update_animation(self):
        # Update Cooldown
        COOLDOWN = 150

        # Update Image dep on curr frame
        self.image = self.animation_list[self.action][self.frame_index]

        # Check if enough time has passed 
        if pygame.time.get_ticks() - self.update_time > COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # If animation done reset:
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 5:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_actions(self, new_action):
        if new_action != self.action:
            if self.shoot_cooldown > 0:  # Check if the player is shooting
                if moving_left or moving_right:  # Check if the player is moving
                    new_action = 4  # Set action to "Shoot Move" (assuming 4 is the index for "Shoot Move")
                else:
                    new_action = 3  # Set action to "Shoot Idle" (assuming 3 is the index for "Shoot Idle")
            self.action = new_action
            # Only reset the frame index if we're not already in the middle of an animation
            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0
                self.update_time = pygame.time.get_ticks()
    
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_actions(5)

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 30
            bullet = Bullet(self.rect.centerx + (self.rect.size[0]*0.5*self.direction), self.rect.centery-20, self.direction)
            bullet_group.add(bullet)

            self.ammo -= 1

    def draw(self):
        # Just draw the image so I don't have to repeat this line of code
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        # Attributes

        super().__init__()
        self.velocity = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # Move bullet
        self.rect.x += (self.direction * self.velocity)

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive:
                enemy.health -= 25
                print(enemy.health)
                self.kill()

player = Entity(250, 250, 3, 3, 20, "player")
enemy = Entity(200, 200, 4, 2, 20, "enemy")

while running:

    clock.tick(FPS)

    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

    player.update()
    player.draw()

    enemy.update()
    enemy.draw()

    # Draw Groups
    bullet_group.update()
    bullet_group.draw(screen)

    # Update the player actions and adjust animation appropriately
    if player.alive:
        if shoot and (not player.in_air):
            player.shoot()
            player.update_actions(3)
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
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_ESCAPE:
                running = False
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
	
    

    pygame.display.update()

pygame.quit()