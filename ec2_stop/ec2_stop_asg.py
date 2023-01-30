import boto3
import csv
import logging

logging.basicConfig(filename='script.log', level=logging.ERROR)

# Read CSV file
with open('instances.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        region = row['Region']
        instance_id = row['Instance ID']
        # Connect to EC2 in specified region
        ec2 = boto3.client('ec2', region_name=region)
        try:
            # Check if instance is part of an autoscaling group
            asg = ec2.describe_auto_scaling_instances(InstanceIds=[instance_id])
            if asg['AutoScalingInstances']:
                # Get autoscaling group name
                asg_name = asg['AutoScalingInstances'][0]['AutoScalingGroupName']
                # Connect to autoscaling in specified region
                asg = boto3.client('autoscaling', region_name=region)
                # Set min, max, and desired instances to 0
                asg.update_auto_scaling_group(AutoScalingGroupName=asg_name, MinSize=0, MaxSize=0, DesiredCapacity=0)
            # Stop instance
            ec2.stop_instances(InstanceIds=[instance_id])
        except Exception as e:
            logging.error(f"Failed to stop instance {instance_id}: {e}")
