import pygame
from pygame import mixer
import os
import random
import csv

mixer.init()
pygame.init()

# Initialise screen
SCREEN_WIDTH = 1000
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
start_game = False
start_intro = False

# colours
BG = (255, 192, 203)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (144, 44, 120)
PINK = (255, 192, 203)
screen.fill(BG)

# Game FPS for Game Loop
clock = pygame.time.Clock()
FPS = 60

# Initalise Other variables
running = True
GRAVITY = 0.75
SCROLL_THRESH = 200
level = 1
MAX_LEVELS = 2
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
screen_scroll = 0
bg_scroll = 0
level_names = ["Level 1 - Press Space to Shoot, E to Throw Grenades, WAD for Everything Else :)", "Level 2 - What Have You Gotten Yourself Into?"]

# Images
bullet_img = pygame.image.load("Shooter Game/Other Assets/bullet.png").convert_alpha()
grenade_img = pygame.image.load("Shooter Game/Other Assets/grenade.png").convert_alpha()
health_box_img = pygame.image.load("Shooter Game/Other Assets/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("Shooter Game/Other Assets/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("Shooter Game/Other Assets/grenade_box.png").convert_alpha()
pine1_img = pygame.image.load("Shooter Game/background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("Shooter Game/background/pine2.png").convert_alpha()
mountain_img = pygame.image.load("Shooter Game/background/mountain.png").convert_alpha()
sky_img = pygame.image.load("Shooter Game/background/sky_cloud.png").convert_alpha()
start_button_img = pygame.image.load("Shooter Game/Buttons/start_btn.png").convert_alpha()
restart_button_img = pygame.image.load("Shooter Game/Buttons/restart_btn.png").convert_alpha()
exit_button_img = pygame.image.load("Shooter Game/Buttons/exit_btn.png").convert_alpha()

# Music and Sounds
choose_music = ["Shooter Game/audio/Cocoon.mp3", "Shooter Game/audio/lmao what.mp3", "Shooter Game/audio/Bad Thing.mp3", "Shooter Game/audio/Paint.mp3"]
pygame.mixer.music.load(choose_music[random.randint(0, 3)])
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound("Shooter Game/audio/jump.wav")
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound("Shooter Game/audio/shot.wav")
shot_fx.set_volume(0.3)
grenade_fx = pygame.mixer.Sound("Shooter Game/audio/grenade.wav")
grenade_fx.set_volume(0.3)

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


# Helper Functions
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for i in range(5):
        screen.blit(sky_img, ((i * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((i * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((i * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((i * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # Create Empty Tile List
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data
    

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
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            # Reset temp list of imgs
            temp_list = []
            num_frames = len(os.listdir(f"Shooter Game/{self.char_type}/{animation}"))
            for i in range(num_frames):
                img = pygame.image.load(f"Shooter Game/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_width() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        # Get First Frame & Rect
        # Action 0 = Idle, Action 1 = Run, Action 2 = Jump etc
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        screen_scroll = 0
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


        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == "enemy":
                    self.direction *= -1
                    self.move_counter = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        self.rect.x += dx  
        self.rect.y += dy


        # check for certain deaths
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
        
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # Check for exit group collision
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # Update scroll based on player pos
        if self.char_type == "player":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    
    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 100
		# update image dep on current frame
        self.image = self.animation_list[self.action][self.frame_index]
		# check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
		# if the animation has run out reset
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_actions(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
			# update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_actions(3)

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 40
            bullet = Bullet(self.rect.centerx + (self.rect.size[0]*0.75*self.direction), self.rect.centery-10, self.direction)
            bullet_group.add(bullet)

            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_actions(0) # idle
                self.idling = True
                self.idling_counter = 50
            elif self.idling == True:
                self.idling_counter -= 1
                if self.idling_counter <= 0:
                    self.idling = False

            if self.idling == False:
                if self.vision.colliderect(player.rect) and (player.rect.x - self.rect.x) * self.direction > 0:
                    self.update_actions(0) # idle
                    self.shoot()
                else:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_actions(1) # run
                    self.move_counter += 1

                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                    else:
                        self.idling_counter -= 1
                        if self.idling_counter <= 0:
                            self.idling = False

        self.rect.x += screen_scroll
    def draw(self):
        # Just draw the image so I don't have to repeat this line of code
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
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
                        player = Entity(x * TILE_SIZE, y * TILE_SIZE, 1.65, 6, 20, 5, "player")
                        health_bar  = HealthBar(10, 40, player.health, player.max_health)
                    elif tile == 16:
                        enemy = Entity(x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20, 0, "enemy")
                        enemy_group.add(enemy)
                        print(f"enemy added at {x}, {y}")
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
                        exits = Exit(x*TILE_SIZE, y*TILE_SIZE, img)
                        exit_group.add(exits)

        return player, health_bar
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll 
            screen.blit(tile[0], tile[1])
class Decoration(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        # Attributes
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        # Attributes
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        # Attributes
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        self.rect.x += screen_scroll
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        # Attributes
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
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
        self.rect.x += (self.direction * self.velocity) + screen_scroll

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
            
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
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
        self.velocity = 7
        self.vel_y = -11
        self.timer = 100
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.velocity
        dy = self.vel_y

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.velocity
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.velocity = 0
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
            

        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # Check that it hit the wall
        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            self.direction *= -1

        # Count down timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
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
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class Button():
	def __init__(self,x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.colour = colour
        self.speed = speed
        self.direction = direction
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1: # On Start
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2: # On Death
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True
        return fade_complete
# Create Screen Fade
intro_fade = ScreenFade(1, BG, 5)
death_fade = ScreenFade(2, PINK, 5)

# Create Buttons
start_button = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_button_img, 1)
exit_button = Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_button_img, 1)
restart_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_button_img, 2)


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

    if start_game == False:
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            running = False

    else:
        draw_bg()
        world.draw()
        # Drawing Text
        if level <= MAX_LEVELS:
            draw_text(level_names[level-1], font, RED, 10, 10)
        draw_text("Ammo:", font, WHITE, 10, 60)
        for x in range(player.ammo):
            screen.blit(bullet_img, (80 + (x * 10), 69))
        #draw_text(f"Health: {player.health}", font, WHITE, 10, 10)
        health_bar.draw(player.health)
        draw_text("Grenades:", font, WHITE, 10, 80)
        for x in range(player.grenade):
            screen.blit(grenade_img, (120 + (x * 15), 87))

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

        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # Update the player actions and adjust animation appropriately
        if player.alive:
            if shoot:
                player.shoot()
            elif grenade and grenade_thrown == False and player.grenade > 0:
                grenade = Grenade(player.rect.centerx + (player.rect.size[0]*0.3*player.direction), player.rect.top, player.direction)
                grenade_group.add(grenade)
                grenade_thrown = True
                player.grenade -= 1
            if player.in_air:
                player.update_actions(2)
            elif moving_left or moving_right:
                player.update_actions(1)
            else:
                player.update_actions(0)

            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            if level_complete:
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f"Shooter Game/Levels/level{level}_data.csv", newline="") as map:
                        reader = csv.reader(map, delimiter=",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)

        else:
            screen_scroll = 0 
            if death_fade.fade():
                for enemy in enemy_group:
                    enemy.update_actions(0)
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    with open(f"Shooter Game/Levels/level{level}_data.csv", newline="") as map:
                        reader = csv.reader(map, delimiter=",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)
                          
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
                jump_fx.play()
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