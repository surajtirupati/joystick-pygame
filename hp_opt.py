import optuna
import torch as th
import numpy as np
from game_env import MyGameEnv
from stable_baselines3 import PPO


class HyperparameterOptimizer:
    def __init__(self, model_str, env_class, reward_function, hyperparams, total_timesteps=10000, n_trials=20):
        """
        Initializes the optimizer.

        :param model_str: String representing the model type, e.g., 'PPO'.
        :param env_class: The environment class to instantiate the environment.
        :param reward_function: The reward function to be used in the environment.
        :param hyperparams: Dictionary of hyperparameters to optimize with their min/max values.
                            Example: {"ent_coef": (0.0001, 0.1), "learning_rate": (1e-5, 0.01)}
        :param total_timesteps: Number of timesteps to train during each trial.
        :param n_trials: Number of trials for the optimization.
        """
        self.model_str = model_str
        self.env_class = env_class
        self.reward_function = reward_function
        self.hyperparams = hyperparams
        self.total_timesteps = total_timesteps
        self.n_trials = n_trials

    def objective(self, trial):
        # Suggest hyperparameters
        hyperparams = {}
        for param_name, (low, high) in self.hyperparams.items():
            if isinstance(low, int) and isinstance(high, int):
                hyperparams[param_name] = trial.suggest_int(param_name, low, high)
            else:
                hyperparams[param_name] = trial.suggest_float(param_name, low, high, log=True)

        # Initialize the environment
        env = self.env_class(reward_function=self.reward_function)

        # Initialize the model with suggested hyperparameters
        model = PPO(
            "MlpPolicy",
            env,
            verbose=0,
            device=th.device("cuda" if th.cuda.is_available() else "cpu"),
            **hyperparams
        )

        # Train the model
        model.learn(total_timesteps=self.total_timesteps)

        # Evaluate the model
        mean_reward = self.evaluate_model(model, env)

        return mean_reward

    def evaluate_model(self, model, env, n_episodes=5):
        """Evaluate the model performance over a number of episodes."""
        all_rewards = []
        for _ in range(n_episodes):
            obs = env.reset()
            done = False
            total_reward = 0
            while not done:
                action, _ = model.predict(obs)
                obs, reward, done, info = env.step(action)
                total_reward += reward
            all_rewards.append(total_reward)
        return np.mean(all_rewards)

    def optimize(self):
        """Optimize the hyperparameters using optuna."""
        study = optuna.create_study(direction="maximize")
        study.optimize(self.objective, n_trials=self.n_trials)

        # Get the best trial
        best_trial = study.best_trial
        print(f"Best trial: Value: {best_trial.value}, Params: {best_trial.params}")

        return best_trial.params


# Example usage:
def train_with_optimized_hyperparameters(model_name):
    optimizer = HyperparameterOptimizer(
        model_str='PPO',
        env_class=MyGameEnv,
        reward_function=MyGameEnv._calculate_rewards_v2,
        hyperparams={
            "ent_coef": (0.0001, 0.1),
            "learning_rate": (1e-5, 0.01),
            "clip_range": (0.1, 0.4)
        },
        total_timesteps=10000,
        n_trials=100
    )

    best_hyperparams = optimizer.optimize()

    # Now train with the best hyperparameters found
    env = MyGameEnv(reward_function=MyGameEnv._calculate_rewards_v2)
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        device=th.device("cuda" if th.cuda.is_available() else "cpu"),
        **best_hyperparams
    )
    model.learn(total_timesteps=100000)

    model.save(model_name)


train_with_optimized_hyperparameters('hp-optimised-bullet-dodger')
