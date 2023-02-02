import boto3
import concurrent.futures
import datetime

def search_cloudtrail_event(user_name, search_string, as_of_datetime):
    client = boto3.client('cloudtrail')
    end_time = as_of_datetime
    start_time = as_of_datetime - datetime.timedelta(hours=24)
    events = client.lookup_events(LookupAttributes=[{'AttributeKey': 'Username', 'AttributeValue': user_name}],
                                  StartTime=start_time, EndTime=end_time)
    filtered_events = [event for event in events['Events'] if search_string in event['CloudTrailEvent']]
    return filtered_events

def search_cloudtrail_events_multithreaded(user_names, search_strings, as_of_datetime):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(search_cloudtrail_event, user_name, search_string, as_of_datetime)
                   for user_name, search_string in zip(user_names, search_strings)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    return results
