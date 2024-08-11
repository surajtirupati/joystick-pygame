import pygame
import random
import time
from config import *
from graphics_fx import character_image, bullet_image, money_image, gunshot_sound, gunshot_channel

class Character:
    def __init__(self):
        self.x = INITIAL_X
        self.y = INITIAL_Y
        self.velocity_x = 0
        self.velocity_y = 0
        self.health = START_HEALTH

    def move(self, velocity_x, velocity_y):
        self.x += velocity_x * SENSITIVITY
        self.y += velocity_y * SENSITIVITY

        # Keep character within bounds
        self.x = max(0, min(WINDOW_SIZE - CHARACTER_WIDTH, self.x))
        self.y = max(0, min(WINDOW_SIZE - CHARACTER_HEIGHT, self.y))

    def draw(self, screen):
        screen.blit(character_image, (self.x, self.y))

    def check_collision(self, other_x, other_y, other_width=None, other_height=None):
        if other_width is None:
            other_width = CHARACTER_WIDTH
        if other_height is None:
            other_height = CHARACTER_HEIGHT
        character_rect = pygame.Rect(self.x, self.y, CHARACTER_WIDTH, CHARACTER_HEIGHT)
        other_rect = pygame.Rect(
            other_x + other_width * (1 - COLLISION_SENSITIVITY) / 2,
            other_y + other_height * (1 - COLLISION_SENSITIVITY) / 2,
            other_width * COLLISION_SENSITIVITY,
            other_height * COLLISION_SENSITIVITY
        )
        return character_rect.colliderect(other_rect)

    def check_bullet_collision(self, bullets):
        for bullet in bullets:
            if self.check_collision(bullet[0], bullet[1], bullet_image.get_width(), bullet_image.get_height()):
                gunshot_sound.play()
                bullets.remove(bullet)
                return True

        return False

    def reset_position(self):
        self.x = INITIAL_X  # Set this to the initial X position
        self.y = INITIAL_Y  # Set this to the initial Y position

class BulletManager:
    def __init__(self):
        self.bullets = []
        self.last_bullet_time = time.time()
        self.next_bullet_interval = random.uniform(BULLET_INTERVAL_MIN, BULLET_INTERVAL_MAX)

    def update(self):
        # Move bullets
        for bullet in self.bullets:
            bullet[1] += BULLET_SPEED
        self.bullets = [bullet for bullet in self.bullets if bullet[1] <= WINDOW_SIZE]

        # Spawn new bullets
        if len(self.bullets) < MAX_BULLETS and time.time() - self.last_bullet_time > self.next_bullet_interval:
            self.spawn_bullet()
            self.last_bullet_time = time.time()
            self.next_bullet_interval = random.uniform(BULLET_INTERVAL_MIN, BULLET_INTERVAL_MAX)

    def spawn_bullet(self):
        bullet_x = random.randint(0, WINDOW_SIZE - bullet_image.get_width())
        bullet_y = 0
        self.bullets.append([bullet_x, bullet_y])

    def draw(self, screen):
        for bullet in self.bullets:
            screen.blit(bullet_image, (bullet[0], bullet[1]))

    def reset(self):
        self.bullets.clear()  # Remove all active bullets

class Money:
    def __init__(self):
        self.x = random.randint(0, WINDOW_SIZE - money_image.get_width())
        self.y = random.randint(0, WINDOW_SIZE - money_image.get_height())
        self.visible = True
        self.respawn_delay = random.uniform(RESPAWN_DELAY_MIN, RESPAWN_DELAY_MAX)
        self.disappear_time = None

    def draw(self, screen):
        if self.visible:
            screen.blit(money_image, (self.x, self.y))

    def collect(self):
        self.visible = False
        self.disappear_time = time.time()
        return random.choice([5, 20, 100])

    def respawn(self):
        if not self.visible and (time.time() - self.disappear_time > self.respawn_delay):
            self.x = random.randint(0, WINDOW_SIZE - money_image.get_width())
            self.y = random.randint(0, WINDOW_SIZE - money_image.get_height())
            self.visible = True  # Ensure visibility is set to True here
            self.respawn_delay = random.uniform(RESPAWN_DELAY_MIN, RESPAWN_DELAY_MAX)


