import random
import numpy as np
import gymnasium as gym
from gymnasium import spaces

class EC2Environment(gym.Env):
    def __init__(self, instance_list, power_data, price_data, workload_profile=None):
        self.instance_list = instance_list
        self.power_data = power_data  # dict: instance_type -> power(W) at full usage
        self.price_data = price_data  # dict: instance_type -> $/hour
        self.workload_profile = workload_profile or self._generate_synthetic_workload()

        self.current_step = 0
        self.current_instance = None
        self.region = 'us-east-1'  # default region

        # Define action and observation spaces
        self.action_space = spaces.Discrete(len(self.instance_list))  # One action per instance type
        self.observation_space = spaces.Box(
            low=np.array([0.0, 0.0, 0.0, 0.0]),  # Min values for [cpu, net, power, price]
            high=np.array([100.0, 1e7, max(self.power_data.values()), max(self.price_data.values())]),
            dtype=np.float32
        )

    def reset(self, seed=None, return_info=False, options=None):
        # Seed the environment for reproducibility
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        self.current_step = 0
        self.current_instance = random.choice(self.instance_list)
        state = self._get_state()

        # Always return a tuple (state, info)
        info = {}  # Empty info dictionary
        return state, info

    def step(self, action):
        """
        Action is the index of the target instance in instance_list.
        """
        prev_instance = self.current_instance
        self.current_instance = self.instance_list[action]

        # Determine if the episode is terminated or truncated
        terminated = self.current_step >= len(self.workload_profile) - 1  # Task is complete
        truncated = False  # No explicit truncation logic in this environment

        if not terminated:
            self.current_step += 1
            next_state = self._get_state()
        else:
            next_state = np.zeros_like(self.observation_space.low)  # Return a dummy state when terminated

        reward = self._calculate_reward(prev_instance, self.current_instance)

        # Optional info dictionary (can be expanded)
        info = {
            "previous_instance": prev_instance,
            "current_instance": self.current_instance,
            "step": self.current_step
        }

        return next_state, reward, terminated, truncated, info

    def _get_state(self):
        workload = self.workload_profile[self.current_step]
        # normalise cpu and network usage
        cpu = workload['cpu'] /100 # normalise to 0-1
        net = workload['network'] /(2*1e7) # normalise to 0-0.5

        power = self.power_data[self.current_instance] * (cpu / 100)
        price = self.price_data[self.current_instance]

        return np.array([cpu, net, power, price])

    def _calculate_reward(self, old_instance, new_instance):
        print("Calculating reward...")
        print(f"Old Instance: {old_instance}, New Instance: {new_instance}")

        # Get the current workload values
        workload = self.workload_profile[self.current_step]
        cpu = workload['cpu']
        print(f"CPU Utilization: {cpu}")

        old_power = self.power_data[old_instance] * (cpu/100)
        new_power = self.power_data[new_instance] * (cpu/100)
        print(f"Old Power: {old_power}, New Power: {new_power}")

        old_cost = self.price_data[old_instance]
        new_cost = self.price_data[new_instance]
        print(f"Old Cost: {old_cost}, New Cost: {new_cost}")

        # reward is energy saved minus extra cost
        power_saved = old_power - new_power
        cost_diff = new_cost - old_cost

        reward = (power_saved * 10) - (cost_diff * 1)  # weight power more
        print(f"Reward: {reward}")
        return reward

    def _generate_synthetic_workload(self):
        profile = []
        for _ in range(100):
            cpu = random.uniform(0, 100)  # percent
            network = random.uniform(1e5, 1e7)  # bytes
            profile.append({'cpu': cpu, 'network': network})
        return profile
