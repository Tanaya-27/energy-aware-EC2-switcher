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
            Period=20,
            Statistics=['Average']
        )

        datapoints = response.get('Datapoints', [])
        if datapoints:
            return datapoints[-1]['Average']#, datapoints[-1]['Unit']
        return 0.0

    def get_all_metrics(self):
        metrics = {
            'CPUUtilization': self.get_cloudwatch_metric('CPUUtilization'),
            'NetworkIn': self.get_cloudwatch_metric('NetworkIn'),
            'NetworkOut': self.get_cloudwatch_metric('NetworkOut')
        }
        return metrics

