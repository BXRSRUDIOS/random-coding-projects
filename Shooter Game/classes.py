import pygame
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        # Temporary Placeholder image for all entities
        super().__init__()
        img = pygame.image.load("Shooter Game/assets/MAIN_CHARACTER.png")
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_width() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self):
        screen.blit(self.image, self.rect)