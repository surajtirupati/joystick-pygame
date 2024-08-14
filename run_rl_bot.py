from game_env import MyGameEnv
from stable_baselines3 import PPO

env = MyGameEnv()

model = PPO.load("game-state-obs-0005-0007-03-reward-v2", env=env)

obs = env.reset()

running = True
while running is True:
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()

    if dones:
        obs = env.reset()
        running = False

