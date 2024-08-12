# **Joystick-Controlled Game with Arduino Input**

This project is a Python-based arcade-style game that uses an Arduino joystick for input. The joystick controls the movement of the main character, and various game elements such as bullets, money, and other objects are managed within the game. The game also includes sound effects that enhance the gaming experience. The purpose of the game is simple - dodge the bullets, and collect the money.

![game](https://github.com/user-attachments/assets/c386f9fb-8d37-4cd3-ab5f-5c5e0b6cac96)


## **Table of Contents**

- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Setup and Installation](#setup-and-installation)
- [Game Controls](#game-controls)
- [Game Flow](#game-flow)
- [Arduino Integration](#arduino-integration)
- [Sound Management](#sound-management)
- [Running the Game](#running-the-game)
- [Troubleshooting](#troubleshooting)
- [Conclusion](#conclusion)

## **Introduction**

This game allows the player to control a character using an Arduino-connected joystick. The character can move around the screen, collect items, and avoid or collide with obstacles like bullets. Upon collision with bullets, sound effects are triggered to provide feedback. The game ends when the player's health reaches zero, and the player is presented with an end screen displaying their final score.

## **Features**

- **Arduino Joystick Integration:** Control the game character using an Arduino-connected joystick.
- **Sound Effects:** Trigger sound effects like a gunshot when the character collides with bullets.
- **Game States:** Includes game running, game over, and end screen states.
- **Score Tracking:** Track and display the player's score.
- **Reset Functionality:** Easily reset the game after it ends to start over.

## **Requirements**

- **Python 3.7+**
- **Pygame Library**
- **Arduino with Joystick Module**
- **USB Connection for Arduino**

## **Setup and Installation**

### **1. Clone the Repository**

```bash
git clone https://github.com/yourusername/joystick-game.git
cd joystick-game
```

### **2. Install Python Dependencies**

Install the required Python libraries:

```bash
pip install pygame pyserial
```

### **3. Arduino Setup**

- Upload the Arduino sketch to your Arduino board. The sketch reads analog joystick input and a switch, sending the data over serial to the computer.
- Ensure the Arduino is connected to your computer via USB and is communicating over the correct serial port.
- Arduino sketch is found in file 'simpleJoystick.ino' -> I am using a Mega 2560 and have connected my x, y, and switch pins to A7, A6, and 50 (digital) respectively.

  Below is an example schematic of the Arduino setup (replace the pins in display with whatever pins you choose - x and y must be analog and switch is digital):
  
![Joystick-Module-interfacing-with-Arduino](https://github.com/user-attachments/assets/f80c43d9-6b76-4572-b112-8d2849896c94)

### **4. Configure the Serial Connection**

In the `arduino_input_handler.py` file, configure the serial port settings to match your Arduino's configuration:

```python
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Update this to match your port and baud rate
```

## **Game Controls**

- **Joystick:** Controls the character’s movement on the screen.
- **Switch Button:** When pressed during the game over screen, the game resets.

## **Game Flow**

### **1. Game Start**

The game starts with the player controlling a character using the joystick.

### **2. Gameplay**

- The player moves the character to avoid bullets and collect money.
- Sound effects are triggered when the character collides with bullets, but sounds will not overlap, ensuring a clear audio experience.
- The score increases when money is collected.

### **3. Game Over**

- When the character's health reaches zero, the game transitions to the end screen, showing the final score.
- Pressing the switch button on the joystick during the end screen resets the game.

## **Arduino Integration**

The `arduino_input_handler.py` file handles the communication between the Arduino and the game. It reads the joystick's X and Y values and the state of the switch button, then translates these inputs into movements and actions within the game.

### **How it Works**

- The Arduino sends serial data to the game, including the joystick's X and Y axis values and the switch button state.
- The game reads this serial data, parses it, and uses it to update the character's position and respond to button presses.
- The file ensures that inputs are handled smoothly, with sound effects playing appropriately during gameplay.

## **Sound Management**

- **Gunshot Sound:** A gunshot sound is played when the character collides with a bullet. 
- **Muting During End Screen:** The gunshot sound is muted when the game transitions to the end screen, ensuring a clean auditory experience during game-over events.

### **Adding New Sounds**

1. Place your sound file in the `/sounds` directory.
2. Load the sound in your game script using `pygame.mixer.Sound('path_to_sound')`.
3. Trigger the sound using `sound.play()` at the appropriate event in the game.

## **Running the Game**

To run the game, ensure all dependencies are installed, your Arduino is connected and sending data, and then execute the main game script:

```bash
python main.py
```

## **Troubleshooting**

- **No Serial Data:** Ensure the correct serial port is selected in the `arduino_input_handler.py` file.
- **Sound Issues:** If sounds aren't playing, ensure your sound files are correctly placed in the `/sounds` directory and that the paths are correctly referenced.
- **Joystick Not Responding:** Verify that the Arduino is properly connected and that the joystick inputs are correctly mapped in the Arduino sketch.

## **Conclusion**

This project demonstrates how to integrate Arduino with Python to create an interactive game. The combination of joystick control and sound effects provides an engaging gaming experience. Feel free to expand and modify the game to suit your needs!
```

This version follows the format you've provided, so you can simply copy and paste it into your `README.md` file on GitHub.
