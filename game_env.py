import gym
from gym import spaces
import numpy as np
from main import Game, WINDOW_SIZE  # Import your game class here
import pygame
import cv2


class MyGameEnv(gym.Env):
    def __init__(self):
        super(MyGameEnv, self).__init__()

        # Initialize your game
        self.game = Game()

        # Define action space: 0 = Up, 1 = Down, 2 = Left, 3 = Right
        self.action_space = spaces.Discrete(4)

        # Define observation space: let's assume it's a flattened version of the game screen
        # Adjust this to match the actual observation format
        self.observation_space = spaces.Box(low=0, high=1, shape=(3, 84, 84), dtype=np.float32)

        # Track the agent's total reward
        self.total_reward = 0

        # Initialize the character's health at the start of the episode
        self.initial_health = self.game.character.health

    def step(self, action):
        # Apply the action to the game
        if action == 0:
            self.game.character.move(0, -1)
        elif action == 1:
            self.game.character.move(0, 1)
        elif action == 2:
            self.game.character.move(-1, 0)
        elif action == 3:
            self.game.character.move(1, 0)

        # Update the game
        self.game.update()

        # Get the new state
        observation = self._get_obs()

        # Calculate reward
        reward = self._calculate_reward()

        # Check if the game is over
        done = self.game.character.health <= 0

        # Return the step information
        info = {}

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
        obs = np.array(pygame.surfarray.array3d(self.game.screen))
        obs = cv2.resize(obs, (84, 84))  # Resize to 84x84 pixels
        obs = np.transpose(obs, (2, 0, 1)).astype(np.float32)  # Convert to (C, H, W) format
        return obs / 255.0  # Normalize to [0, 1]

    def _calculate_reward(self):
        # Calculate the reward based on the game state:
        reward = 0

        # Reward for collecting money
        if self.game.collection_message_visible:
            reward += 10

        # Penalty for getting hit by a bullet
        if self.game.character.health < self.initial_health:
            reward -= 1 * (self.initial_health - self.game.character.health)
            self.initial_health = self.game.character.health  # Update for subsequent steps

        return reward

