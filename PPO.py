from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
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
    model.learn(total_timesteps=100000)

    # Save the model
    model.save(model_name)


if __name__ == '__main__':
    entropy_coefficient = 0.01
    learn_rate = 0.0007
    c_range = 0.45
    train_PPO(ent_coeff=entropy_coefficient, learning_rate=learn_rate, clip_range=c_range)
