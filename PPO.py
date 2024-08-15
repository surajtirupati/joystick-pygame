import os
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback
import matplotlib.pyplot as plt

from game_env import MyGameEnv
import torch as th

import warnings


def train_PPO(policy='MlpPolicy', model_name='ppo_pixel_obs', ent_coeff=0.0, learning_rate=0.003, clip_range=0.2):
    # Device
    device = th.device("cuda" if th.cuda.is_available() else "cpu")

    # Suppress warnings
    warnings.filterwarnings("ignore")

    # Initialize your custom environment
    env = MyGameEnv()

    # Check the environment to make sure it's correctly implemented
    check_env(env)

    # Create the RL agent
    model = PPO(policy, env, verbose=1, device=device, ent_coef=ent_coeff, learning_rate=learning_rate, clip_range=clip_range)

    # Train the agent
    model.learn(total_timesteps=1000000)

    # Save the model
    model.save(model_name)


def train_ppo_v2(policy='MlpPolicy', model_name='ppo_bullet_avoidance_reward_v2', ent_coeff=0.0, learning_rate=0.003, clip_range=0.2, reward_function=MyGameEnv._calculate_reward):
    device = th.device("cuda" if th.cuda.is_available() else "cpu")

    env = MyGameEnv(reward_function=reward_function)

    model = PPO(policy, env, verbose=1, device=device, ent_coef=ent_coeff, learning_rate=learning_rate, clip_range=clip_range)

    performance_logger = PerformanceLoggerCallback(trial_number=0, params=0)

    model.learn(total_timesteps=100000, callback=performance_logger)

    model.save(model_name)

    performance_logger.save_results(reward_filename=f'plots/{model_name}_rewards.png', length_filename=f'plots/{model_name}_lengths.png')


def retrain_PPO(model_name='game-state-obs-001-0007-03', ent_coeff=0.0, learning_rate=0.003, clip_range=0.2):

    env = MyGameEnv()

    model = PPO.load(model_name, env=env)

    model.learn(total_timesteps=10000000)

    model.save("game-state-obs-001-0007-03-retrained")


class PerformanceLoggerCallback(BaseCallback):
    def __init__(self, trial_number, params, save_dir='plots', verbose=0):
        super(PerformanceLoggerCallback, self).__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
        self.current_episode_reward = 0
        self.current_episode_length = 0
        self.trial_number = trial_number
        self.params = params
        self.save_dir = save_dir

    def _on_step(self) -> bool:
        # Accumulate reward and length
        self.current_episode_reward += self.locals['rewards'][0]
        self.current_episode_length += 1

        # Check if the episode is done
        if self.locals['dones'][0]:
            # Log the results
            self.episode_rewards.append(self.current_episode_reward)
            self.episode_lengths.append(self.current_episode_length)

            # Reset for the next episode
            self.current_episode_reward = 0
            self.current_episode_length = 0

        return True

    def plot_results(self):
        # Plot rewards
        plt.figure(figsize=(12, 5))
        plt.plot(self.episode_rewards, label='Episode Reward')
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.title('Episode Rewards Over Time')
        plt.legend()
        plt.show()

        # Plot episode lengths
        plt.figure(figsize=(12, 5))
        plt.plot(self.episode_lengths, label='Episode Length')
        plt.xlabel('Episode')
        plt.ylabel('Length')
        plt.title('Episode Lengths Over Time')
        plt.legend()
        plt.show()

    def save_results(self):
        """Save the performance plots as PNG files."""
        # Plot rewards
        plt.figure(figsize=(12, 5))
        plt.plot(self.episode_rewards, label='Episode Reward')
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.title(f'Reward Over Time - Trial {self.trial_number}\n{self.params}')
        plt.legend()
        plt.savefig(os.path.join(self.save_dir, f'reward_trial_{self.trial_number}.png'))
        plt.close()

        # Plot episode lengths
        plt.figure(figsize=(12, 5))
        plt.plot(self.episode_lengths, label='Episode Length')
        plt.xlabel('Episode')
        plt.ylabel('Length')
        plt.title(f'Episode Length Over Time - Trial {self.trial_number}\n{self.params}')
        plt.legend()
        plt.savefig(os.path.join(self.save_dir, f'length_trial_{self.trial_number}.png'))
        plt.close()


if __name__ == '__main__':
    store_as = 'game-state-obs-0005-0007-03-reward-v3-bullet-dodge'
    entropy_coefficient = 0.1
    learn_rate = 0.0005
    c_range = 0.3
    train_ppo_v2(model_name=store_as, ent_coeff=entropy_coefficient, learning_rate=learn_rate, clip_range=c_range, reward_function=MyGameEnv._calculate_reward)

    #  retrain_PPO()
