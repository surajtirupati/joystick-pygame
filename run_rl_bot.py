from game_env import MyGameEnv
from stable_baselines3 import PPO

env = MyGameEnv()

model = PPO.load("ppo_game_agent", env=env)

obs = env.reset()

for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()

    if dones:
        obs = env.reset()
