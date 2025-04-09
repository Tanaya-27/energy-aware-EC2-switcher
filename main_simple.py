# main.py

from metrics import MetricCollector
from decision_heuristic import InstanceRecommender
import os
import requests
import time

def get_instance_metadata():
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

if __name__ == "__main__":
    while True:
        instance_id = get_instance_metadata()
        collector = MetricCollector(instance_id)
        recommender = InstanceRecommender()

        metrics = collector.get_all_metrics()

        print("Collected metrics:", metrics)
        decision = recommender.evaluate(metrics)
        print("Decision:", decision)
        time.sleep(20)