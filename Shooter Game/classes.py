import pygame
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

GRAVITY = 0.75

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, velocity, char_type):
        # Temporary Placeholder image for all entities
        super().__init__()
        # Main Attributes
        self.alive = True
        self.velocity = velocity
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
        animation_types = ["Idle", "Run", "Jump"]
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
        # Action 0 = Idle, Action 1 = Walk, Action 2 = Jump
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

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
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

    def update_actions(self, new_action):
        # We will update the action now
        if new_action != self.action:
            self.action = new_action
            # Update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    
    def draw(self):
        # Just draw the image so I don't have to repeat this line of code
        self.update_animation()
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
