import boto3
from datetime import datetime

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
        if "Task failed to start" in message:
            task_id, stop_code = message.split(" stopped with stop code ")
            task_id = task_id.split(" ")[-1]
            results.append({
                "task_id": task_id,
                "stop_code": stop_code
            })

    return results