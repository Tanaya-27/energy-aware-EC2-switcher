import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metrics import MetricCollector
from decision_heuristic import InstanceRecommender
from switcher import Switcher
import boto3
import time

def main(region_name='us-east-1'):
    ec2 = boto3.client('ec2', region_name=region_name)
    recommender = InstanceRecommender()
    switcher = Switcher()

    while True:
        instances = switcher.get_all_instances(region_name)
        for instance in instances:
            instance_id = instance['InstanceId']
            current_type = instance['InstanceType']
            state = instance['State']

            #skip stopped or terminated instances
            if state not in ['running']:
                continue

            collector = MetricCollector(instance_id, region_name)
            metrics = collector.get_all_metrics()

            print("Collected metrics:", metrics)

            recommendation = recommender.evaluate(metrics)
            print(f"{instance_id} ({current_type}): {recommendation}")

            if recommendation == "switch to larger":
                new_type = switcher.get_adjacent_instance_type(current_type, direction='up')
                if new_type != current_type:
                    switcher.switch_instance_type(ec2, instance_id, new_type)

            elif recommendation == "switch to smaller":
                new_type = switcher.get_adjacent_instance_type(current_type, direction='down')
                if new_type != current_type:
                    switcher.switch_instance_type(ec2, instance_id, new_type)

        time.sleep(60)  # TODO wait 5 minutes between checks
    
if __name__ == "__main__":
    main()
