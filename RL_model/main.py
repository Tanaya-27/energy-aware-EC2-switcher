import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metrics import MetricCollector
from learning_agent import RLAgent
from RL_environment import EC2Environment
from switcher import Switcher
import boto3
import time

def main(region_name='us-east-1'):
    ec2 = boto3.client('ec2', region_name=region_name)

    # define instance types, power data, and price data for the RL environment
    instance_list = ["t2.micro", "t2.small", "t2.medium", "t2.large"]
    power_data = {"t2.micro": 8.0, "t2.small": 12.0, "t2.medium": 20.0, "t2.large": 32.0}
    price_data = {"t2.micro": 0.0116, "t2.small": 0.023, "t2.medium": 0.0464, "t2.large": 0.0928}

    # create the RL environment
    env = EC2Environment(
        instance_list=instance_list,
        power_data=power_data,
        price_data=price_data,
        # max_steps=20000  #training episode length
    )

    # initialize the RL agent
    agent = RLAgent(env)

    # train the RL model with random examples
    print("Training the RL model...")
    agent.train(timesteps=20000)
    print("Training complete. Model saved.")

    # load the trained model
    agent.load()

    # track recommendation history
    recommendation_counters = {}

    # start monitoring and managing EC2 instances
    print("Starting instance management loop...")
    while True:
        # get all running instances
        instances = Switcher.get_all_instances(region_name)
        for instance in instances:
            instance_id = instance['InstanceId']
            current_type = instance['InstanceType']
            state = instance['State']

            # skip stopped or terminated instances
            if state not in ['running']:
                continue

            # collect metrics for the instance
            collector = MetricCollector(instance_id, region_name)
            metrics = collector.get_all_metrics()
            print(f"Collected metrics for {instance_id}: {metrics}")

            # prepare state for the RL model
            cpu = metrics.get('CPUUtilization', 0.0)
            net = metrics.get('NetworkIn', 0.0) + metrics.get('NetworkOut', 0.0)
            power = power_data[current_type] * (cpu / 100)
            price = price_data[current_type]

            if(cpu == 0.0):
                print(f"Skipping {instance_id}; CPU utilization not collected.\n")
                continue

            state = [cpu, net, power, price]

            #use the RL model to predict the next action
            action = agent.predict(state)
            recommended_type = instance_list[action]
            print(f"RL model recommendation for {instance_id}: {recommended_type}")

            # add prediciton to recommendation counter as a voting system

            if instance_id not in recommendation_counters:
                recommendation_counters[instance_id] = {
                    "last_direction": None,
                    "count": 0
                }
            
            if(recommended_type != current_type):
                # Determine the direction of the current recommendation
                current_index = instance_list.index(current_type)
                recommended_index = instance_list.index(recommended_type)
                direction = "up" if recommended_index > current_index else "down"

                # Check if the direction matches the last direction
                if recommendation_counters[instance_id]["last_direction"] == direction:
                    recommendation_counters[instance_id]["count"] += 1
                else:
                    # Reset the counter if the direction changes
                    recommendation_counters[instance_id] = {
                        "last_direction": direction,
                        "count": 1
                    }
                print(f"{recommendation_counters[instance_id]["count"]} votes to switch {direction} for {instance_id}\n(current: {current_type}, recommended: {recommended_type})\n")

                # switch only if recommendation is same 3 times and not already of that type
                if (recommendation_counters[instance_id]["count"] >= 3):
                    print(f"Switching {instance_id} from {current_type} to {recommended_type}\n")
                    Switcher.switch_instance_type(ec2, instance_id, recommended_type)

                    # reset counter after switching
                    recommendation_counters[instance_id] = {
                        "last_direction": None,
                        "count": 0
                    }
            else:
                # reset counter as no switch needed
                recommendation_counters[instance_id] = {
                    "last_direction": None,
                    "count": 0
                }
                print(f"No switch needed for {instance_id} (current: {current_type}, recommended: {recommended_type})\n")

        time.sleep(10)  # TODO wait 5 minutes between checks
    
if __name__ == "__main__":
    main()
