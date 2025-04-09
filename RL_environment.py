import random
import numpy as np

class EC2Environment:
    def __init__(self, instance_list, power_data, price_data, workload_profile=None):
        self.instance_list = instance_list
        self.power_data = power_data  # dict: instance_type -> power(W) at full usage
        self.price_data = price_data  # dict: instance_type -> $/hour
        self.workload_profile = workload_profile or self._generate_synthetic_workload()

        self.current_step = 0
        self.current_instance = None
        self.region = 'us-east-1'  # default region

    def reset(self):
        self.current_step = 0
        self.current_instance = random.choice(self.instance_list)
        state = self._get_state()
        return state

    def step(self, action):
        """
        Action is the index of the target instance in instance_list
        """
        prev_instance = self.current_instance
        self.current_instance = self.instance_list[action]
        self.current_step += 1

        next_state = self._get_state()
        reward = self._calculate_reward(prev_instance, self.current_instance)
        done = self.current_step >= len(self.workload_profile)

        return next_state, reward, done, {}

    def _get_state(self):
        workload = self.workload_profile[self.current_step]
        cpu = workload['cpu']
        net = workload['network']

        power = self.power_data[self.current_instance] * (cpu / 100)
        price = self.price_data[self.current_instance]

        return np.array([cpu, net, power, price])

    def _calculate_reward(self, old_instance, new_instance):
        old_power = self.power_data[old_instance]
        new_power = self.power_data[new_instance]

        old_cost = self.price_data[old_instance]
        new_cost = self.price_data[new_instance]

        # reward is energy saved minus extra cost
        power_saved = old_power - new_power
        cost_diff = new_cost - old_cost

        reward = (power_saved * 10) - (cost_diff * 1)  # weight power more
        return reward

    def _generate_synthetic_workload(self):
        profile = []
        for _ in range(100):
            cpu = random.uniform(10, 90)  # percent
            network = random.uniform(1e5, 1e7)  # bytes
            profile.append({'cpu': cpu, 'network': network})
        return profile
