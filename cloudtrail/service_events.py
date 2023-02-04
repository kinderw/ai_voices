import boto3
import json
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
        try:
            message_json = json.loads(message)
            if "stopCode" in message_json and "stoppedReason" in message_json:
                stop_code = message_json["stopCode"]
                stopped_reason = message_json["stoppedReason"]
                results.append({
                    "stop_code": stop_code,
                    "stopped_reason": stopped_reason
                })
        except json.JSONDecodeError:
            continue

    return results