import boto3
import csv
import logging
from concurrent.futures import ThreadPoolExecutor

def stop_old_instances(csv_file):
    # Set up a logger to log any errors that occur
    logging.basicConfig(filename='stop_old_instances.log', level=logging.ERROR)

    # Use ThreadPoolExecutor to parallelize the execution of the function for different instances
    with ThreadPoolExecutor() as executor:
        futures = []
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                instance_id = row['instance_id']
                account = row['account']
                region = row['region']
                session = boto3.Session(profile_name=account)
                futures.append(executor.submit(stop_instance, session, instance_id, region))

        for future in futures:
            try:
                future.result()
            except Exception as e:
                logging.error(f"An error occurred while stopping instance {instance_id} in region {region} for account {account}: {e}")
                print(f"An error occurred while stopping instance {instance_id} in region {region} for account {account}")

def stop_instance(session, instance_id, region):
    ec2 = session.client('ec2', region_name=region)
    ec2.stop_instances(InstanceIds=[instance_id])
    print(f'Instance {instance_id} in region {region} stopped.')

csv_file = '\test\mockdata\inst.csv'
stop_old_instances(csv_file)