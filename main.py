import os
import requests
import csv
from urllib.parse import urljoin
from cron_descriptor import get_description

api_base_url = os.environ.get('LOOKER_API_BASE_URL')
if not api_base_url:
    api_base_url = input('Enter Looker API base URL: ')
api_client_id = os.environ.get('LOOKER_CLIENT_ID')
if not api_client_id:
    api_client_id = input('Enter Looker API client ID: ')
api_client_secret = os.environ.get('LOOKER_CLIENT_SECRET')
if not api_client_secret:
    api_client_secret = input('Enter Looker API client secret: ')

api_url = urljoin(api_base_url, "api/")

token_response = requests.post(
    urljoin(api_url, "login"), data={"client_id": api_client_id, "client_secret": api_client_secret})

token_response.raise_for_status()
access_token = token_response.json()['access_token']

headers = {'Authorization': 'token ' + access_token}

# get details of all the alerts and schedules (they are separate objects) that exist in that Looker account,
# and exporting them to a single, clean human-readable .csv file
# once extracted, alerts and schedules should be treated as the same thing,
# with a column that flags the object type and extra columns for their unique attributes (e.g. thresholds for alerts, scheduled_plan_destination.format, for schedules)


schedules_response = requests.get(
    urljoin(api_url, "4.0/scheduled_plans"), headers=headers)
schedules_response.raise_for_status()
schedules = schedules_response.json()

alerts_response = requests.get(
    urljoin(api_url, "4.0/alerts/search"), headers=headers)

alerts_response.raise_for_status()
alerts = alerts_response.json()

fields_alerts = alerts[0].keys() if len(alerts) > 0 else []
fields_schedules = schedules[0].keys() if len(schedules) > 0 else []

results_columns = [
    'type',
    'name',
    'owner',
    'schedule_trigger',
    'destinations_count',
    'destinations',
    'metrics',
    'looks_tiles',
    'conditions',
    'sampling_frequency',
    'message_content',
    'communication_tool',
    'engagement_usage',
]
# 2 CSV files, one for actual results, one for statistics

result_file = open('results.csv', 'w')
results_writer = csv.DictWriter(result_file, fieldnames=results_columns)
results_writer.writeheader()

for alert in alerts:
    formatted_alert = {
        'type': 'alert',
        'name': alert['custom_title'],
        'owner': alert['owner_display_name'],
        'schedule_trigger': 0,  # <- TODO
        'destinations_count': len(alert['destinations']),
        'destinations': alert['destinations'],
        'metrics': alert['field']['name'],
        'looks_tiles': 0,  # <- TODO
        'conditions': alert['comparison_type'] + ' ' + str(alert['threshold']),
        'sampling_frequency': get_description(alert['cron']),
        'message_content': '',
        'communication_tool': '',
        'engagement_usage': '??',
    }
    results_writer.writerow(formatted_alert)
for schedule in schedules:
    formatted_schedule = {
        'type': 'schedule',
        'name': schedule['name'],
        'owner': schedule['user']['display_name'],
        'schedule_trigger': 0,  # <- TODO
        'destinations_count': len(schedule['scheduled_plan_destination']),
        'destinations': schedule['scheduled_plan_destination'],
        'metrics': schedule['name'],  # <- TODO
        'looks_tiles': 0,  # <- TODO
        'conditions': '',
        'sampling_frequency': get_description(schedule['crontab']),
        'message_content': '',
        'communication_tool': '',
        'engagement_usage': '??',
    }
    results_writer.writerow(formatted_schedule)

result_file.close()

# Statistics file

metrics_names = map(lambda alert: alert['field']['name'], alerts)

# Destination names are either email addresses or integration IDs
destination_names = []
for alert in alerts:
    for destination in alert['destinations']:
        destination_name = destination.get(
            'email_address', destination.get("action_hub_integration_id"))
        if destination_name:
            destination_names.append(destination_name)

stats_obj = {
    'alerts_count': len(alerts),
    'schedules_count': len(schedules),
    # count of unique metrics names
    'metrics_count': len(list(set(metrics_names))),
    # count of unique destinations names
    'destinations_count': len(list(set(destination_names))),
}

stats_file = open('stats.csv', 'w')
stats_writer = csv.DictWriter(stats_file, fieldnames=list(stats_obj.keys()))
stats_writer.writeheader()
stats_writer.writerow(stats_obj)

stats_file.close()
