import pygame
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, velocity, char_type, no_frames):
        # Temporary Placeholder image for all entities
        super().__init__()
        # Main Attributes
        self.velocity = velocity
        self.direction = 1
        self.flip = False
        self.char_type = char_type
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        # Load Images
        for i in range(1, no_frames+1):
            img = pygame.image.load(f"Shooter Game/{self.char_type}/{self.char_type}{i}.png")
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_width() * scale)))
            self.animation_list.append(img)

        # Get First Frame & Rect
        self.image = self.animation_list[self.frame_index]
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

        self.rect.x += dx  
        self.rect.y += dy
    
    def update_animation(self):
        # Update Cooldown
        COOLDOWN = 100

        # Update Image dep on curr frame
        self.image = self.animation_list[self.frame_index]

        # Check if enough time has passed 
        if pygame.time.get_ticks() - self.update_time > COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # If animation done reset:
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

    
    def draw(self):
        # Just draw the image so I don't have to repeat this line of code
        self.update_animation()
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
