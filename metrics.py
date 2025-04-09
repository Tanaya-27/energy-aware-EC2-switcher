'''
This script collects metrics from AWS CloudWatch and estimates power consumption.
It uses the boto3 library to interact with AWS services and requests to fetch instance metadata.  
'''
import boto3
import datetime
import requests

class MetricCollector:
    def __init__(self, instance_id, region_name='us-east-1'):
        self.instance_id = instance_id
        self.cloudwatch = boto3.client('cloudwatch', region_name=region_name)

    def get_cloudwatch_metric(self, metric_name, namespace='AWS/EC2'):
        end_time = datetime.datetime.now(datetime.timezone.utc)
        start_time = end_time - datetime.timedelta(minutes=5)

        response = self.cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=[{'Name': 'InstanceId', 'Value': self.instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=['Average']
        )

        datapoints = response.get('Datapoints', [])
        if datapoints:
            return datapoints[-1]['Average']
        return 0.0

    def get_all_metrics(self):
        metrics = {
            'CPUUtilization': self.get_cloudwatch_metric('CPUUtilization'),
            'NetworkIn': self.get_cloudwatch_metric('NetworkIn'),
            'NetworkOut': self.get_cloudwatch_metric('NetworkOut')
        }

        return metrics
    
    # TODO use PowerAPI — replace with real API
    # def estimate_power_consumption(self):
    #     
    #     try:
    #         response = requests.get("http://localhost:8000/power")
    #         return response.json().get('power', 0.0)
    #     except:
    #         return None

# testing metrics by printing them out
def get_instance_metadata():
    try:
        # Step 1: Request a token for IMDSv2
        token_response = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=2
        )
        token_response.raise_for_status()
        token = token_response.text

        # Step 2: Use the token to fetch the instance ID
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


if __name__ == "__main__":
    instance_id = get_instance_metadata()
    if not instance_id:
        print("Failed to retrieve instance ID. Exiting.")
    else:
        collector = MetricCollector(instance_id)

    collector = MetricCollector(instance_id)

    metrics = collector.get_all_metrics()
    # metrics['power'] = collector.estimate_power_consumption()

    print("Collected metrics:", metrics)
