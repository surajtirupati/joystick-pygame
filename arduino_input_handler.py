import threading
import serial
from config import *

class Joystick:
    def __init__(self):
        self.joystick_x = 503
        self.joystick_y = 499
        self.joystick_switch = 1
        self.velocity_x = 0
        self.velocity_y = 0

    def start_reading(self):
        serial_thread = threading.Thread(target=self.read_serial, daemon=True)
        serial_thread.start()

    def read_serial(self):
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                try:
                    parts = line.split(',')
                    x_part = parts[0].split(':')[1]
                    y_part = parts[1].split(':')[1]
                    switch = parts[2].split(':')[1]
                    self.joystick_x = int(x_part)
                    self.joystick_y = int(y_part)
                    self.joystick_switch = int(switch)

                except (IndexError, ValueError):
                    pass

    def get_velocity(self):
        dead_zone = 100
        inverted_x = 1023 - self.joystick_x
        inverted_y = 1023 - self.joystick_y

        if inverted_x < (512 - dead_zone):
            self.velocity_x -= ACCELERATION
        elif inverted_x > (512 + dead_zone):
            self.velocity_x += ACCELERATION
        else:
            self.velocity_x *= DRIFT

        if inverted_y < (512 - dead_zone):
            self.velocity_y -= ACCELERATION
        elif inverted_y > (512 + dead_zone):
            self.velocity_y += ACCELERATION
        else:
            self.velocity_y *= DRIFT

        self.velocity_x = max(-MAX_SPEED, min(MAX_SPEED, self.velocity_x))
        self.velocity_y = max(-MAX_SPEED, min(MAX_SPEED, self.velocity_y))

        return self.velocity_x, self.velocity_y
