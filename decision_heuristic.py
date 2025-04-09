# decision_heuristic.py

class InstanceRecommender:
    def __init__(self, cpu_weight=0.7, net_weight=0.3):
        self.cpu_weight = cpu_weight
        self.net_weight = net_weight

        # Simple thresholds for example
        self.thresholds = {
            'cpu_upper': 70,     # percent
            'cpu_lower': 20,     # percent
            'net_upper': 5000000, # bytes (5MB)
            'net_lower': 50000,  # bytes (50KB)
        }

    def evaluate(self, metrics):
        if metrics['CPUUtilization'] > self.thresholds['cpu_upper'] and metrics['NetworkIn'] + metrics['NetworkOut'] > self.thresholds['net_upper']:
            return "Consider switching to a smaller instance type"
        if metrics['CPUUtilization'] < self.thresholds['cpu_lower'] and metrics['NetworkIn'] + metrics['NetworkOut'] < self.thresholds['net_lower']:
            return "Consider switching to a larger instance type"
        else:
            return "Instance type is acceptable"

