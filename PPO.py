from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from game_env import MyGameEnv
import torch as th

import warnings

# Device
device = th.device("cuda" if th.cuda.is_available() else "cpu")

# Suppress warnings
warnings.filterwarnings("ignore")

# Initialize your custom environment
env = MyGameEnv()

# Check the environment to make sure it's correctly implemented
check_env(env)

# Create the RL agent
model = PPO("MlpPolicy", env, verbose=1, device=device)

# Train the agent
model.learn(total_timesteps=100000)

# Save the model
model.save("ppo_game_agent")

# To load and continue training or use the agent:
model = PPO.load("ppo_game_agent", env=env)


