import boto3
import requests

# Ordered list of instance sizes (can expand this as needed)
INSTANCE_ORDER = ['t2.micro', 't2.small', 't2.medium', 't2.large']

def get_master_instance():
        try:
            # request a token for IMDSv2
            token_response = requests.put(
                "http://169.254.169.254/latest/api/token",
                headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
                timeout=2
            )
            token_response.raise_for_status()
            token = token_response.text

            # use the token to fetch the instance ID
            metadata_response = requests.get(
                "http://169.254.169.254/latest/meta-data/instance-id",
                headers={"X-aws-ec2-metadata-token": token},
                timeout=2
            )
            metadata_response.raise_for_status()
            return metadata_response.text
        except requests.RequestException as e:
            print(f"Error fetching instance metadata: {e}")
            return None

class Switcher:
    @staticmethod
    def get_all_instances(region_name='us-east-1'):
        ec2 = boto3.client('ec2', region_name=region_name)
        response = ec2.describe_instances()
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # exclude master instance
                if instance['InstanceId'] != get_master_instance():
                    instances.append({
                        'InstanceId': instance['InstanceId'],
                        'InstanceType': instance['InstanceType'],
                        'State': instance['State']['Name']
                    })
        return instances

    @staticmethod
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

    @staticmethod
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