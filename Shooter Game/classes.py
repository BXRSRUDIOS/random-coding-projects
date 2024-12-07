import pygame
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, velocity, char_type):
        # Temporary Placeholder image for all entities
        super().__init__()
        self.velocity = velocity
        self.direction = 1
        self.flip = False
        self.char_type = char_type
        img = pygame.image.load("Shooter Game/assets/MAIN_CHARACTER.png")
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_width() * scale)))
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
    
    def draw(self):
        # Just draw the image so I don't have to repeat this line of code
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
