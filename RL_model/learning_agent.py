from RL_environment import EC2Environment
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import DummyVecEnv

# define instance types, power data, and price data for the RL environment
instance_list = ["t2.micro", "t2.small", "t2.medium", "t2.large"]
power_data = {"t2.micro": 8.0, "t2.small": 12.0, "t2.medium": 20.0, "t2.large": 32.0}
price_data = {"t2.micro": 0.0116, "t2.small": 0.023, "t2.medium": 0.0464, "t2.large": 0.0928}

# instantiate environment
env = EC2Environment(
    instance_list=instance_list,
    power_data=power_data,
    price_data=price_data,
    # max_steps=5  # short test episode
)

class RLAgent:
    def __init__(self, env):
        self.env = DummyVecEnv([lambda: env])  # wrap for vectorized environment
        self.model = PPO("MlpPolicy", self.env, verbose=1)

    def train(self, timesteps=20000):
        self.model.learn(total_timesteps=timesteps)
        self.model.save("ppo_instance_switcher")

    def load(self, path="ppo_instance_switcher"):
        self.model = PPO.load(path)

    def predict(self, state):
        action, _states = self.model.predict(state)
        return action