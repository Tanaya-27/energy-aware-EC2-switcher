## Realtime EC2 Instance Switching to Lower Carbon Footprint By Increasing Energy Efficiency

Cloud computing, including related tools such as LLMs, have gained attention for their
negative impact on the environment, the primary sustainability problem being their huge
energy consumption [1]. This stems from the massive physical data centers required, and is
made much worse by the lack of energy efficiency tools available to users. A user running an
EC2 instance should be able to dynamically adapt to the most energy efficient alternative
in real time.

This problem can be solved by an Energy-Aware Real-Time Instance Switcher (EARTIS),
which automatically detects and resizes the instance (or changes its type, region etc.) based
on the current state. The model, a Python script that will run alongside the user’s work-
load, will involve three simple layers: live data monitoring [2], decision making for instance
selection, and automation for live switching (or potentially notification to user).
Layer one can involve any of the following metrics:
 - AWS CloudWatch [3] → Real-time monitoring of CPU utilization, memory, network
bandwidth, etc.
 - PowerAPI [4] → Estimate instance power consumption based on utilization.
 - AWS Pricing Info → Fetch real-time spot and on-demand instance pricing.

Layer two can apply weights to the above metrics, to formulate a heuristic that decides
the most efficient instance type. With that, if a switch is necessary, layer three can imple-
ment it, either by notifying the user of a preferred switch, or implementing boto3 in Python
to resize the instance [5].

The frequency of monitoring can be adapted to further avoid energy waste. For exam-
ple, if polling, data can be collected at larger intervals (several minutes up to an hour, rather
than seconds) to drastically decrease energy consumption from measurement. This interval
can even be dynamic, and change based on the current state; for instance, a shorter instance
is CPU utilization is approaching the threshold. Alternatively, polling can be replaced by
an even-driven monitoring system, for example taking measurements only when CPU usage
exceeds a threshold. AWS CloudWatch Alarms can be used as an alert. To further reduce
overhead, the decision model should be kept to a low complexity.

This solution is unique in that it tailors auto-switching instances to the highest energy
efficiency, while existing models such as AWS Auto Scaling [6] focuses only on performance
metrics, scaling up simply to meet demand. The EARTIS system will extend these capabil-
ities, focusing on real-time dynamic switching based on a number of factors that prioritize
sustainability.

### References:

[1] Steven Gonzalez Monserrate. The staggering ecological impacts of
computation and the cloud. https://thereader.mitpress.mit.edu/the-staggering-ecological-impacts-of-computation-and-the-cloud/, 02 2022.

[2] Benjamin DAVY. Estimating aws ec2 instances power
consumption. https://medium.com/teads-engineering/estimating-aws-ec2-instances-power-consumption-c9745e347959, 09 2021.

[3] Cloudwatch - boto3 1.36.14 documentation. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html, 2025.

[4] PowerAPI . Powerapi. https://powerapi.org/, 2024.

[5] modify instance attribute - boto3 1.36.14 documentation. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/modify_instance_attribute.html, 2025.

[6] Amazon Web Services. Aws auto scaling. https://aws.amazon.com/autoscaling/,
2018.
