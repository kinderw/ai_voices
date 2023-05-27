import boto3
from datetime import datetime, timedelta
import csv
import concurrent.futures

# AWS credentials and region configuration
aws_access_key_id = 'YOUR_ACCESS_KEY_ID'
aws_secret_access_key = 'YOUR_SECRET_ACCESS_KEY'
aws_region = 'us-east-1'

# S3 bucket and file configuration
s3_bucket_name = 'ami-exception-list-us-east-1'
s3_file_name = 'ami_exception_list.csv'

# Establish connection to AWS EC2 and S3
ec2_client = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

# Retrieve the exception list from S3
s3_response = s3_client.get_object(Bucket=s3_bucket_name, Key=s3_file_name)
s3_data = s3_response['Body'].read().decode('utf-8').splitlines()

# Parse the exception list CSV
exception_list = list(csv.reader(s3_data))

# Get the current date and calculate the date 60 days ago
current_date = datetime.now().date()
expiration_date = current_date - timedelta(days=60)

# Retrieve all EC2 instances
response = ec2_client.describe_instances()
instances = response['Reservations']

# Function to process each EC2 instance
def process_instance(instance):
    ami_id = instance['ImageId']
    instance_id = instance['InstanceId']
    
    # Retrieve instance details including tags
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance_details = response['Reservations'][0]['Instances'][0]
    
    # Retrieve the "support email" tag value
    support_email = ""
    for tag in instance_details['Tags']:
        if tag['Key'] == 'support email':
            support_email = tag['Value']
            break
    
    # Retrieve AMI details
    response = ec2_client.describe_images(ImageIds=[ami_id])
    ami_details = response['Images'][0]
    ami_creation_date = ami_details['CreationDate']
    
    # Parse the creation date and check if it's older than 60 days
    ami_creation_date = datetime.strptime(ami_creation_date, '%Y-%m-%dT%H:%M:%S.%f%z').date()
    
    if ami_creation_date < expiration_date:
        ami_expired = True
        print(f"AMI ID: {ami_id} for Instance ID: {instance_id} is older than 60 days.")
    else:
        ami_expired = False
        print(f"AMI ID: {ami_id} for Instance ID: {instance_id} is within 60 days.")
    
    exception_found = False
    for exception in exception_list:
        name_prefix = exception[0]
        oldest_date = datetime.strptime(exception[1], '%Y-%m-%d').date()
        
        if ami_name.startswith(name_prefix) and oldest_date < current_date:
            if not ami_expired:
                print(f"AMI ID: {ami_id} for Instance ID: {instance_id} matches exception '{name_prefix}' but is not older than {oldest_date}.")
            else:
                print(f"AMI ID: {ami_id} for Instance ID: {instance_id} matches exception '{name_prefix}' and is older than {oldest_date}.")
                exception_found = True
                break
    
    if exception_found:
        print(f"Support Email: {support_email}")
        print("Tagging instance with AmiExpired: TRUE")
        # Tag the instance with AmiExpired: TRUE
        ec2_client.create_tags(Resources=[instance_id], Tags=[{'Key': 'AmiExpired', 'Value': 'TRUE'}])
    else:
        print("Tagging instance with AmiExpired: FALSE")
        # Tag the instance with AmiExpired: FALSE
        ec2_client.create_tags(Resources=[instance_id], Tags=[{'Key': 'AmiExpired', 'Value': 'FALSE'}])
    
    print("------------------------------")

# Process each EC2 instance concurrently using multithreading
with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(process_instance, instances)
