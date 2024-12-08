import pygame
import os
import random
import csv

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
grenade = False
grenade_thrown = False

# Initialise background
BG = (144, 44, 120)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
screen.fill(BG)

# Game FPS for Game Loop
clock = pygame.time.Clock()
FPS = 60

# Initalise Other variables
running = True
GRAVITY = 0.75
level = 2
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21

# Images
bullet_img = pygame.image.load("Shooter Game/Other Assets/bullet.png").convert_alpha()
grenade_img = pygame.image.load("Shooter Game/Other Assets/grenade.png").convert_alpha()
health_box_img = pygame.image.load("Shooter Game/Other Assets/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("Shooter Game/Other Assets/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("Shooter Game/Other Assets/grenade_box.png").convert_alpha()

# store tiles in a list
img_list = []
for i in range(TILE_TYPES):
    img = pygame.image.load(f"Shooter Game/Tiles/{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img
}

# Create Sprite Groups
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


font = pygame.font.Font("Shooter Game/Other Assets/font2.ttf", 20)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, velocity, ammo, grenade, char_type):
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
        self.grenade = grenade
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

        # Other Attributes (mainly for enemy)
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0
        
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
        #update animation
        ANIMATION_COOLDOWN = 100
		#update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
		#check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
		#if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 5:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_actions(self, new_action):
        if new_action != self.action:
            if self.shoot_cooldown > 0:  # Check if the player is shooting
                if moving_left or moving_right:  # Check if the player is moving
                    new_action = 4  # Set action to "Shoot Move"
                else:
                    new_action = 3  # Set action to "Shoot Idle"
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
            self.shoot_cooldown = 40
            bullet = Bullet(self.rect.centerx + (self.rect.size[0]*0.75*self.direction), self.rect.centery-10, self.direction)
            bullet_group.add(bullet)

            self.ammo -= 1

    def ai(self):
        if self.alive and player.alive:
            if random.randint(1, 200) == 1 and self.idling == False:
                self.idling = True
                self.update_actions(0)
                self.idling_counter = 75
            if self.vision.colliderect(player.rect):
                self.update_actions(0) 
                self.shoot()
            else:
                if self.idling == False:
                    if self.alive and player.alive:
                        if self.direction == 1:
                            ai_moving_right = True
                        else:
                            ai_moving_right = False
                        ai_moving_left = not ai_moving_right
                        self.move(ai_moving_left, ai_moving_right)
                        self.update_actions(1)
                        self.move_counter += 1
                        self.vision.center = (self.rect.centerx + (self.direction * 75), self.rect.centery)

                        if self.move_counter > TILE_SIZE:
                            self.move_counter *= -1
                            self.direction *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
    def draw(self):
        # Just draw the image so I don't have to repeat this line of code
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        # Iterate through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(x*TILE_SIZE, y*TILE_SIZE, img)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(x*TILE_SIZE, y*TILE_SIZE, img)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Entity(x*TILE_SIZE, y*TILE_SIZE, 1.65, 3, 20, 5, "player")
                        health_bar  = HealthBar(10, 10, player.health, player.max_health)
                    elif tile == 16:
                        enemy = Entity(x*TILE_SIZE, y*TILE_SIZE, 1.65, 1, 20, 0, "enemy")
                        enemy_group.add(enemy)
                    elif tile == 17:
                        item_box = ItemBox(x*TILE_SIZE, y*TILE_SIZE, "Ammo")
                        item_box_group.add(item_box)
                    elif tile == 18:
                        item_box = ItemBox(x*TILE_SIZE, y*TILE_SIZE, "Grenade")
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox(x*TILE_SIZE, y*TILE_SIZE, "Health")
                        item_box_group.add(item_box)
                    elif tile == 20:
                        exit = Exit(x*TILE_SIZE, y*TILE_SIZE, img)
                        exit_group.add(exit)

        return player, health_bar
    def draw(self):
        for tile in self.obstacle_list:
            screen.blit(tile[0], tile[1])
class Decoration(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        # Attributes
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

class Water(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        # Attributes
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        # Attributes
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        # Attributes
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenade += 3
            self.kill()

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, ratio*150, 20))

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
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        # Attributes

        super().__init__()
        self.velocity = 10
        self.vel_y = -11
        self.timer = 100
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.velocity
        dy = self.vel_y

        # Check for collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.velocity = 0

        self.rect.x += dx
        self.rect.y += dy

        # Check that it hit the wall
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1

        # Count down timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y)
            explosion_group.add(explosion)

            # Damaging Entities
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
                    enemy.health -= 50

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        # Attributes
        super().__init__()
        self.images = []
        self.scale = 1
        for num in range(1, 6):
            img = pygame.image.load(f"Shooter Game/Explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_width() * self.scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

# Creating an empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# Creating the actual world
with open(f"Shooter Game/Levels/level{level}_data.csv", newline="") as map:
    reader = csv.reader(map, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

while running:

    clock.tick(FPS)

    draw_bg()
    world.draw()
    # Drawing Text
    draw_text("Ammo", font, WHITE, 10, 35)
    for x in range(player.ammo):
        screen.blit(bullet_img, (80 + (x * 10), 45))
    #draw_text(f"Health: {player.health}", font, WHITE, 10, 10)
    health_bar.draw(player.health)
    draw_text("Grenades:", font, WHITE, 10, 60)
    for x in range(player.grenade):
        screen.blit(grenade_img, (120 + (x * 15), 66))

    #Draw Player & Enemy
    player.update()
    player.draw()

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    # Update Groups
    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    item_box_group.update()
    decoration_group.update()
    water_group.update()
    exit_group.update()

    # Draw Groups
    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    item_box_group.draw(screen)
    decoration_group.draw(screen)
    water_group.draw(screen)
    exit_group.draw(screen)

    # Update the player actions and adjust animation appropriately
    if player.alive:
        if shoot:
            player.shoot()
            player.update_actions(3)
        elif grenade and grenade_thrown == False and player.grenade > 0:
            grenade = Grenade(player.rect.centerx + (player.rect.size[0]*0.3*player.direction), player.rect.top, player.direction)
            grenade_group.add(grenade)
            grenade_thrown = True
            player.grenade -= 1
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
            if event.key == pygame.K_e:
                grenade = True
                grenade_thrown = False
            if event.key == pygame.K_ESCAPE:
                running = False
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_e:
                grenade = False

    pygame.display.update()

pygame.quit()