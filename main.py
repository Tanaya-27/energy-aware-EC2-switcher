from metrics import MetricCollector
from decision_heuristic import InstanceRecommender
import boto3
import time

# Ordered list of instance sizes (can expand this as needed)
INSTANCE_ORDER = ['t2.micro', 't2.small', 't2.medium', 't2.large']

def get_all_instances(region_name='us-east-1'):
    ec2 = boto3.client('ec2', region_name=region_name)
    response = ec2.describe_instances()
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append({
                'InstanceId': instance['InstanceId'],
                'InstanceType': instance['InstanceType'],
                'State': instance['State']['Name']
            })
    return instances

def get_adjacent_instance_type(current_type, direction='up'):
    try:
        index = INSTANCE_ORDER.index(current_type)
        if direction == 'up' and index < len(INSTANCE_ORDER) - 1:
            return INSTANCE_ORDER[index + 1]
        elif direction == 'down' and index > 0:
            return INSTANCE_ORDER[index - 1]
        else:
            return current_type  # Already at boundary
    except ValueError:
        print(f"Unknown instance type: {current_type}")
        return current_type

def switch_instance_type(ec2, instance_id, new_type):
    try:
        print(f"Switching {instance_id} to {new_type}")
        ec2.stop_instances(InstanceIds=[instance_id])
        waiter = ec2.get_waiter('instance_stopped')
        waiter.wait(InstanceIds=[instance_id])

        ec2.modify_instance_attribute(InstanceId=instance_id, Attribute='instanceType', Value=new_type)
        ec2.start_instances(InstanceIds=[instance_id])
        print(f"Instance {instance_id} successfully switched to {new_type}")
    except Exception as e:
        print(f"Failed to switch {instance_id}: {e}")

def main(region_name='us-east-1'):
    ec2 = boto3.client('ec2', region_name=region_name)
    recommender = InstanceRecommender()

    while True:
        instances = get_all_instances(region_name)
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
                new_type = get_adjacent_instance_type(current_type, direction='up')
                if new_type != current_type:
                    switch_instance_type(ec2, instance_id, new_type)

            elif recommendation == "switch to smaller":
                new_type = get_adjacent_instance_type(current_type, direction='down')
                if new_type != current_type:
                    switch_instance_type(ec2, instance_id, new_type)

        time.sleep(60)  # TODO wait 5 minutes between checks
    
if __name__ == "__main__":
    main()
