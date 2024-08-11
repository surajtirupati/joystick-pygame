import pygame
import serial

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Define colors
RED = (255, 0, 0)
PINK = (255, 192, 203)
WHITE = (255, 255, 255)

# Display settings
BOARD_SIZE = 12
SQUARE_SIZE = 100
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE

# Character settings
CHARACTER_WIDTH = 200
CHARACTER_HEIGHT = 200
SENSITIVITY = 2
ACCELERATION = 0.5
MAX_SPEED = 10
DRIFT = 0.90
START_HEALTH = 500
INITIAL_X = WINDOW_SIZE // 2 - CHARACTER_WIDTH // 2
INITIAL_Y = WINDOW_SIZE - CHARACTER_HEIGHT - 10

# Bullet settings
BULLET_SPEED = 8
MAX_BULLETS = 5
BULLET_INTERVAL_MIN = 0.5
BULLET_INTERVAL_MAX = 2.0
BULLET_DAMAGE = 10

# Money settings
RESPAWN_DELAY_MIN = 1
RESPAWN_DELAY_MAX = 2

# Bank settings
BANK_SIZE = WINDOW_SIZE // 8
BANK_X = WINDOW_SIZE - BANK_SIZE - 50
BANK_Y = 10

# Collision sensitivity factor (0.0 to 1.0)
COLLISION_SENSITIVITY = 0.2  # 0.5 means the bounding box is half the size of the bullet/money image

# Background settings
NUM_TILES = 2
TILE_HEIGHT = WINDOW_SIZE // NUM_TILES
TILE_WIDTH = WINDOW_SIZE
SCROLL_SPEED = 2

# Colour tuples
BLOOD_RED = (120, 6, 6)
MONEY_GREEN = (62, 156, 53)

# Serial connection (joystick)
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600

# Initialize serial connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)  # Replace 'COM3' with your Arduino's serial port
except Exception as e:
    raise RuntimeError(f'Error with Serial Monitor: {e}')
