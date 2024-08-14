import gym
from gym import spaces
import numpy as np
from main import Game, WINDOW_SIZE, ACCELERATION, MAX_SPEED, DRIFT, MAX_BULLETS  # Import your game class here
import pygame
import cv2


class MyGameEnv(gym.Env):
    def __init__(self, reward_function=None):
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

        # Initialize visited positions set
        self.visited_positions = set()

        # Initialize the character's health at the start of the episode
        self.initial_health = self.game.character.health

        # Set the reward function, defaulting to _calculate_reward if not provided
        self.reward_function = reward_function or self._calculate_reward

    def step(self, action, reward_function=None):
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

        # Calculate reward
        if reward_function is None:
            reward_function = self._calculate_reward  # Use default reward function

            # Calculate reward
        reward = reward_function()

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
        reward = 0

        # Reward for collecting money
        reward += self._reward_for_collecting_money()

        # Penalty for getting hit by a bullet
        reward += self._penalty_for_getting_hit()

        # Additional penalties and incentives
        reward += self._penalty_for_line_of_fire()
        reward += self._penalty_for_being_in_upper_half()
        reward += self._penalty_for_loitering_near_edges()
        reward += self._penalty_for_going_too_fast()
        reward += self._reward_for_being_in_center()
        # reward += self._reward_for_dodging_bullets()
        reward += self._penalty_for_time_since_money_appeared()
        reward += self._reward_for_proximity_to_money()

        return reward

    def _exploration_reward(self):
        # Track positions visited and reward for new positions
        position = (int(self.game.character.x // 50), int(self.game.character.y // 50))
        if position not in self.visited_positions:
            self.visited_positions.add(position)
            return 5  # Reward for exploring a new area
        return 0

    def _reward_for_collecting_money(self):
        """Reward for collecting money. This should be the highest incentive."""
        if self.game.collection_message_visible:
            return 50  # High reward for collecting money
        return 0

    def _penalty_for_getting_hit(self):
        """Penalty for getting hit by a bullet, with a larger penalty for the final hit."""
        if self.game.character.health < self.initial_health:
            if self.game.character.health <= 0:
                return -100  # Large penalty for the final death blow
            else:
                self.initial_health = self.game.character.health
                return -20  # Standard penalty for getting hit
        return 0

    def _penalty_for_line_of_fire(self):
        """Penalty for being in the line of fire, scaled by proximity to the bullet."""
        penalty = 0
        for bullet in self.game.bullet_manager.bullets:
            bullet_x, bullet_y = bullet[0], bullet[1]
            if abs(bullet_x - self.game.character.x) < 50:  # Within a certain x-distance of the bullet
                if bullet_y < self.game.character.y:  # Bullet is above and moving towards the character
                    penalty -= 10  # Stronger penalty for being in the direct path
                elif bullet_y > self.game.character.y and abs(bullet_y - self.game.character.y) < 100:
                    penalty -= 5  # Lesser penalty if the bullet is already past but close
        return penalty

    def _penalty_for_being_in_upper_half(self):
        """Penalty for staying in the upper half of the screen, which is closer to the source of bullets."""
        if self.game.character.y < WINDOW_SIZE / 2:
            return -5  # Moderate penalty for staying in the upper half
        return 0

    def _penalty_for_loitering_near_edges(self):
        """Penalty for loitering near the edges of the screen."""
        penalty = 0
        edge_distance_threshold = 100  # Distance from the edge to be considered "loitering"
        if (self.game.character.x < edge_distance_threshold or
                self.game.character.x > WINDOW_SIZE - edge_distance_threshold or
                self.game.character.y < edge_distance_threshold or
                self.game.character.y > WINDOW_SIZE - edge_distance_threshold):
            penalty -= 10  # Penalty for staying near the edges
        return penalty

    def _penalty_for_going_too_fast(self):
        """Penalty for moving too fast, which might indicate panic or less control."""
        speed = np.sqrt(self.game.character.velocity_x ** 2 + self.game.character.velocity_y ** 2)
        max_speed_threshold = MAX_SPEED * 0.8  # Adjust threshold as needed
        if speed > max_speed_threshold:
            return -5  # Penalty for going too fast
        return 0

    def _reward_for_being_in_center(self):
        """Small reward for staying near the center of the screen, encouraging exploration."""
        center_x, center_y = WINDOW_SIZE // 2, WINDOW_SIZE // 2
        distance_from_center = np.sqrt((self.game.character.x - center_x) ** 2 +
                                       (self.game.character.y - center_y) ** 2)
        max_distance_from_center = np.sqrt(center_x ** 2 + center_y ** 2)
        return 10 * (1 - distance_from_center / max_distance_from_center)  # Scaled reward based on proximity to center

    def _reward_for_dodging_bullets(self):
        """Reward for successfully dodging bullets."""
        reward = 0
        for bullet in self.game.bullet_manager.bullets:
            bullet_x, bullet_y = bullet[0], bullet[1]
            if abs(bullet_x - self.game.character.x) < 50 and bullet_y > self.game.character.y:
                if bullet_y > self.game.character.y + 100:  # Successfully dodged bullet
                    reward += 5  # Small reward for dodging
        return reward

    def _penalty_for_time_since_money_appeared(self):
        """Penalty for the time elapsed since the money appeared but hasn't been collected."""
        if self.game.money.visible:
            elapsed_time = (pygame.time.get_ticks() - self.game.money.appear_time) / 1000  # Convert to seconds
            return -0.1 * elapsed_time  # Penalty increases over time
        return 0

    def _reward_for_proximity_to_money(self):
        """Reward based on the proximity of the character to the money, scaled to be as important as avoiding bullets."""
        # Calculate the Euclidean distance between the character and the money
        distance = np.sqrt((self.game.character.x - self.game.money.x) ** 2 +
                           (self.game.character.y - self.game.money.y) ** 2)

        # Normalize the distance (assuming max distance is the diagonal of the screen)
        max_distance = np.sqrt(WINDOW_SIZE ** 2 + WINDOW_SIZE ** 2)
        normalized_distance = distance / max_distance  # Normalize to [0, 1]

        # Invert and scale the distance to a reward in the range [0, 20]
        reward = 20 * (1 - normalized_distance)

        return reward

    ### Reward v2 - only for dodging bullets

    def _calculate_rewards_v2(self):
        """Reward function focused on bullet avoidance and survival."""
        reward = 0

        # Apply penalties based on proximity to bullets
        reward += self._penalty_for_proximity_to_bullets_v2()

        # Apply a severe penalty for getting hit by a bullet
        reward += self._penalty_for_getting_hit_by_bullet_v2()

        # Reward for surviving longer
        reward += self._reward_for_survival_v2()

        return reward

    def _penalty_for_proximity_to_bullets_v2(self):
        """Penalty based on the proximity of the character to bullets, with stronger penalties for closer proximity."""
        penalty = 0

        # Loop through all bullets and calculate the penalty based on distance
        for bullet in self.game.bullet_manager.bullets:
            distance = np.sqrt((self.game.character.x - bullet[0]) ** 2 +
                               (self.game.character.y - bullet[1]) ** 2)

            # Normalize the distance (assuming max distance is the diagonal of the screen)
            max_distance = np.sqrt(WINDOW_SIZE ** 2 + WINDOW_SIZE ** 2)
            normalized_distance = distance / max_distance  # Normalize to [0, 1]

            # Inverse the distance to create a stronger penalty for closer distances
            proximity_penalty = -50 * (1 - normalized_distance)  # Scale the penalty as needed

            penalty += proximity_penalty

        return penalty

    def _penalty_for_getting_hit_by_bullet_v2(self):
        """Severe penalty for actually getting hit by a bullet."""
        if self.game.character.health < self.initial_health:
            hit_penalty = -200  # Large penalty for getting hit by a bullet
            self.initial_health = self.game.character.health  # Update for subsequent hits
            return hit_penalty
        return 0

    def _reward_for_survival_v2(self):
        """Reward that increases with the agent's survival time."""
        # Calculate the time survived (you can use the game’s internal clock or a simple counter)
        time_survived = pygame.time.get_ticks() / 1000  # Time in seconds

        # Scale the reward by time; for example, reward increases by 10 points per second survived
        survival_reward = 10 * time_survived

        return survival_reward
