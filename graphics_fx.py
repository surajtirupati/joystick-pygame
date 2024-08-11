import pygame
from config import *

# Load sounds
gunshot_sound = pygame.mixer.Sound('sounds/gunshot.mp3')
gunshot_channel = pygame.mixer.Channel(0)
gunshot_sound.set_volume(0.1)

# Load images
character_image = pygame.image.load('images/50.png')
bullet_image = pygame.image.load('images/bullet.png')
money_image = pygame.image.load('images/money.png')
bank_image = pygame.image.load('images/bank.png')
background_image = pygame.image.load('images/background.jpg')
end_image = pygame.image.load('images/end.png')
heart_image = pygame.image.load('images/heart.png')

# Scale images
character_image = pygame.transform.scale(character_image, (CHARACTER_WIDTH, CHARACTER_HEIGHT))
bullet_image = pygame.transform.scale(pygame.transform.flip(bullet_image, False, True), (bullet_image.get_width() // 5, bullet_image.get_height() // 5))
money_image = pygame.transform.scale(money_image, (money_image.get_width() // 5, money_image.get_height() // 5))
bank_image = pygame.transform.scale(bank_image, (BANK_SIZE, BANK_SIZE))
background_image = pygame.transform.scale(background_image, (TILE_WIDTH, TILE_HEIGHT))
heart_image = pygame.transform.scale(heart_image, (50, 50))
end_image = pygame.transform.scale(end_image, (300, 380))

def draw_tiled_background(screen, offset_y):
    screen.blit(background_image, (0, offset_y))
    screen.blit(background_image, (0, offset_y + TILE_HEIGHT))
    if offset_y > 0:
        screen.blit(background_image, (0, offset_y - TILE_HEIGHT))

def draw_chessboard(screen, offset):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = RED if (row + col) % 2 == 0 else PINK
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, (row * SQUARE_SIZE) + offset, SQUARE_SIZE, SQUARE_SIZE))

def draw_character(screen, character_x, character_y):
    screen.blit(character_image, (character_x, character_y))

def draw_money(screen, money_x, money_y):
    screen.blit(money_image, (money_x, money_y))

def draw_collection_message(screen, message_visible, collection_message, money_x, money_y):
    if message_visible:
        font = pygame.font.Font(None, 36)
        message_text = font.render(collection_message, True, (255, 255, 0))
        screen.blit(message_text, (money_x, money_y - 40))

def draw_score(screen, score, bank_x, bank_y):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: ${score}", True, (255, 255, 255))
    score_x = bank_x + (BANK_SIZE - score_text.get_width()) // 2
    score_y = bank_y + BANK_SIZE + 5
    screen.blit(score_text, (score_x, score_y))

def draw_bank(screen, bank_x, bank_y):
    screen.blit(bank_image, (bank_x, bank_y))
