import boto3
from datetime import datetime
import re

def get_ecs_task_failure_stop_codes(service_name, start_time, end_time):
    client = boto3.client("logs")

    response = client.filter_log_events(
        logGroupName='/aws/ecs/ecs-agent',
        startTime=int((start_time - datetime(1970, 1, 1)).total_seconds() * 1000),
        endTime=int((end_time - datetime(1970, 1, 1)).total_seconds() * 1000),
        filterPattern=f"{service_name}",
    )

    results = []
    for event in response['events']:
        message = event['message']
        if "TaskFailedToStart" in message or "EssentialContainerExited" in message:
            task_id_match = re.search(r"task (\w+)", message)
            stop_code_match = re.search(r"stopCode ([\w:]+)", message)
            if task_id_match and stop_code_match:
                task_id = task_id_match.group(1)
                stop_code = stop_code_match.group(1)
                results.append({
                    "task_id": task_id,
                    "stop_code": stop_code
                })

    return results