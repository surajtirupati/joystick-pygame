import gym
from gym import spaces
import numpy as np
from main import Game, WINDOW_SIZE, ACCELERATION, MAX_SPEED, DRIFT, MAX_BULLETS  # Import your game class here
import pygame
import cv2


class MyGameEnv(gym.Env):
    def __init__(self):
        super(MyGameEnv, self).__init__()

        # Initialize your game
        self.game = Game()

        # Define action space: 0 = Up, 1 = Down, 2 = Left, 3 = Right
        self.action_space = spaces.Box(low=-1, high=1, shape=(2,), dtype=np.float32)

        # Define observation space dimensions
        player_state_dim = 4  # x, y, velocity_x, velocity_y
        bullet_state_dim = 3  # x, y, velocity for each bullet
        money_state_dim = 3  # x, y, visibility

        # Total observation space size
        self.obs_dim = player_state_dim + bullet_state_dim * MAX_BULLETS + money_state_dim

        # Define observation space
        self.observation_space = spaces.Box(
            low=-1024,  # Assuming all values can theoretically be any real number
            high=1024,  # The real range will depend on the specific game mechanics
            shape=(self.obs_dim,),
            dtype=np.float32
        )

        # Track the agent's total reward
        self.total_reward = 0

        # Initialize the character's health at the start of the episode
        self.initial_health = self.game.character.health

    def step(self, action):
        action = np.array(action)  # Ensure action is a NumPy array

        # Convert action from [-1, 1] to joystick range [0, 1023]
        joystick_x = int((action[0] + 1) * 511.5)  # Convert to [0, 1023]
        joystick_y = int((action[1] + 1) * 511.5)  # Convert to [0, 1023]

        # Invert the joystick values to match your game logic
        inverted_x = 1023 - joystick_x
        inverted_y = 1023 - joystick_y

        # Implement the velocity update logic similar to get_velocity method
        dead_zone = 100

        if inverted_x < (512 - dead_zone):
            self.game.character.velocity_x -= ACCELERATION
        elif inverted_x > (512 + dead_zone):
            self.game.character.velocity_x += ACCELERATION
        else:
            self.game.character.velocity_x *= DRIFT

        if inverted_y < (512 - dead_zone):
            self.game.character.velocity_y -= ACCELERATION
        elif inverted_y > (512 + dead_zone):
            self.game.character.velocity_y += ACCELERATION
        else:
            self.game.character.velocity_y *= DRIFT

        # Ensure the velocity is within the allowed range
        self.game.character.velocity_x = max(-MAX_SPEED, min(MAX_SPEED, self.game.character.velocity_x))
        self.game.character.velocity_y = max(-MAX_SPEED, min(MAX_SPEED, self.game.character.velocity_y))

        # Bridge between GameEnv and Game - game env calculates
        self.game.update(velocity_x=self.game.character.velocity_x, velocity_y=self.game.character.velocity_y)

        # Get the new state
        observation = self._get_obs()

        # Calculate the reward
        reward = self._calculate_reward()

        # Check if the game is over
        done = self.game.character.health <= 0

        # Return the step information
        info = {}

        # Render
        self.render('human')

        return observation, reward, done, info

    def reset(self):
        # Reset the game to the initial state
        self.game.reset_game()

        # Reset the initial health
        self.initial_health = self.game.character.health

        # Return the initial observation
        return self._get_obs()

    def render(self, mode='human'):
        # Render the game to the screen
        self.game.render()
        pygame.display.flip()

    def _get_obs(self):
        # Get the player's state
        player_state = np.array([self.game.character.x, self.game.character.y, self.game.character.velocity_x,
                                 self.game.character.velocity_y], dtype=np.float32)

        # Get the states of all bullets (limit to max_bullets)
        bullets = np.zeros((MAX_BULLETS, 3), dtype=np.float32)  # Initialize with zeros as float32
        for i, bullet in enumerate(self.game.bullet_manager.bullets[:MAX_BULLETS]):
            if len(bullet) >= 3:
                bullets[i] = np.array([bullet[0], bullet[1], bullet[2]], dtype=np.float32)  # x, y, velocity

        # Get the money state
        money_state = np.array([self.game.money.x, self.game.money.y, int(self.game.money.visible)], dtype=np.float32)

        # Concatenate all parts into a single observation vector
        obs = np.concatenate([player_state, bullets.flatten(), money_state])

        return obs

    def _calculate_reward(self):
        # Calculate the reward based on the game state:
        reward = 0

        # Reward for collecting money
        if self.game.collection_message_visible:
            reward += 50

        # Penalty for getting hit by a bullet
        if self.game.character.health < self.initial_health:
            reward -= 10
            self.initial_health = self.game.character.health  # Update for subsequent steps

        if self.game.character.health <= 0:
            reward -= 50

        return reward

