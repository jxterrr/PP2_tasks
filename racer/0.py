import pygame
import random
import time
import os

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# finding the way to the folder "resources"
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
RES_PATH = os.path.join(BASE_PATH, "resources")

def get_path(filename):
    return os.path.join(RES_PATH, filename)

# downloading resources 
try:
    image_background = pygame.image.load(get_path('road.png'))
    image_player = pygame.image.load(get_path('Player.png'))
    image_enemy = pygame.image.load(get_path('Enemy.png'))
    coin_image = pygame.image.load(get_path('coin.png')).convert_alpha()
    
    pygame.mixer.music.load(get_path('background.wav'))
    sound_crash = pygame.mixer.Sound(get_path('crash.wav'))
except Exception as e:
    print(f"Error: couldn't find the folder 'resources'! {e}")
    pygame.quit()
    exit()

font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = image_player
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.move_ip(-5, 0)
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH: self.rect.move_ip(5, 0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = image_enemy
        self.rect = self.image.get_rect()
        self.reset()
    def reset(self):
        self.rect.top = -100
        self.rect.left = random.randint(0, WIDTH - self.rect.width)
    def move(self):
        self.rect.move_ip(0, 7)
        if self.rect.top > HEIGHT: self.reset()

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(coin_image, (40, 40))
        self.rect = self.image.get_rect()
        self.reset()
    def reset(self):
        self.rect.top = -50
        self.rect.left = random.randint(0, WIDTH - self.rect.width)
    def move(self):
        self.rect.move_ip(0, 5)
        if self.rect.top > HEIGHT: self.reset()

# initialization of the objects 
player = Player()
enemy = Enemy()
coin = Coin()
enemies = pygame.sprite.Group(enemy)
coins = pygame.sprite.Group(coin)
all_sprites = pygame.sprite.Group(player, enemy, coin)

collected = 0
pygame.mixer.music.play(-1)
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    player.move()
    for sprite in all_sprites:
        if sprite != player: sprite.move()

    screen.blit(image_background, (0, 0))
    score_txt = font_small.render(f"Score: {collected}", True, (0, 0, 0))
    screen.blit(score_txt, (WIDTH - 100, 10))

    for sprite in all_sprites:
        screen.blit(sprite.image, sprite.rect)

    if pygame.sprite.spritecollideany(player, coins):
        collected += 1
        coin.reset()

    if pygame.sprite.spritecollideany(player, enemies):
        pygame.mixer.music.stop()
        sound_crash.play()
        screen.fill((255, 0, 0))
        screen.blit(font.render("GAME OVER", True, (0, 0, 0)), (30, 250))
        pygame.display.flip()
        time.sleep(2)
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()