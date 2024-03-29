import json
import os
import requests
import csv
from urllib.parse import urljoin
from cron_descriptor import get_description


def format_dashboard_elements(dashboard_elements):
    formatted_elements = []
    for element in dashboard_elements:
        if not element['query']:
            continue

        formatted_element = {
            'view': element['query']['view'],
            'fields': element['query']['fields'],
            'pivots': element['query']['pivots'],
            'filters': element['query']['filters'],
            'sorts': element['query']['sorts'],
            'single_value_title': element['query']['vis_config'].get('single_value_title', ''),
            'note_text': element['note_text'],
            'model': element['query']['model'],
        }
        formatted_elements.append(formatted_element)
    return formatted_elements


def get_dashboard_elements(dashboard_id, headers):
    dashboard_response = requests.get(
        urljoin(api_url, "4.0/dashboards/"+dashboard_id), headers=headers)
    dashboard_response.raise_for_status()
    dashboard = dashboard_response.json()

    dashboard_elements = dashboard['dashboard_elements']
    return dashboard_elements

def get_dashboard_title(dashboard_id, headers):
  dashboard_response = requests.get(
      urljoin(api_url, "4.0/dashboards/"+dashboard_id), headers=headers)
  dashboard_response.raise_for_status()
  dashboard = dashboard_response.json()

  dashboard_title = dashboard['title']
  return dashboard_title


def format_alert_destinations(destinations, headers):
    destination_types = []
    channel_types = []

    for destination in destinations:
        destination_types.append(
            'email' if destination['destination_type'] == 'EMAIL' else 'slack')

        if destination.get('action_hub_integration_id'):
            integration_response = requests.get(urljoin(
                api_url, "4.0/integrations/"+destination['action_hub_integration_id']), headers=headers)
            integration_response.raise_for_status()
            integration = integration_response.json()
            channel_types.append(integration['label'])
        else:
            channel_types.append('')

    return {
        'destination_type': ",".join(list(set(destination_types))),
        'channel_type': ",".join(list(set(channel_types))),
    }


def format_schedule_destinations(destinations):
    destination_types = []
    channel_types = []
    formats = []
    messages = []

    for destination in destinations:
        destination_types.append(
            'email' if destination['type'] == 'email' else 'slack')
        if destination['format']:
            formats.append(destination['format'])
        if destination['message']:
            messages.append(destination['message'])

        # parameters is either an empty string or a JSON string (empty string as fallback)
        parameters = destination.get('parameters', '')
        if parameters != '':
            parsed_parameters = json.loads(parameters)
            channel_types.append(parsed_parameters.get(
                'channelType', ''))
            messages.append(parsed_parameters.get(
                'initial_comment', ''))

    return {
        'destination_type': ",".join(list(set(destination_types))),
        'channel_type': ",".join(list(set(channel_types))),
        'format': ",".join(formats),
        'message': ",".join(messages),
    }


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
    'schedule_or_data_trigger',
    'id',
    'name',
    'owner',
    'destinations_count',
    'destination_type',
    'channel_type',
    'format',
    'message',
    'metric_monitored',
    'conditions',
    'sampling_frequency',
    'source_tile_or_dashboard',
    'engagement_usage',
]
# 2 CSV files, one for actual results, one for statistics

result_file = open('results.csv', 'w')
results_writer = csv.DictWriter(result_file, fieldnames=results_columns)
results_writer.writeheader()

for alert in alerts:
    dashboard_element_response = requests.get(urljoin(
        api_url, "4.0/dashboard_elements/"+str(alert['dashboard_element_id'])), headers=headers)
    dashboard_element_response.raise_for_status()
    dashboard_element = dashboard_element_response.json()

    dashboard_elements = get_dashboard_elements(
        str(dashboard_element['dashboard_id']), headers)

    formatted_alert = {
        'id': alert['id'],
        'schedule_or_data_trigger': "alert",
        'name': alert['custom_title'],
        'owner': alert['owner_display_name'],
        'destinations_count': len(alert['destinations']),
        'metric_monitored': alert['field']['name'],
        'source_tile_or_dashboard': format_dashboard_elements(dashboard_elements),
        'conditions': alert['comparison_type'] + ' ' + str(alert['threshold']),
        'sampling_frequency': get_description(alert['cron']),
        'engagement_usage': '??',
    }
    formatted_alert.update(format_alert_destinations(
        alert['destinations'], headers=headers))
    results_writer.writerow(formatted_alert)

for schedule in schedules:
    dashboard_elements = get_dashboard_elements(
        str(schedule['dashboard_id']), headers)

    dashboard_title = get_dashboard_title(
        str(schedule['dashboard_id']), headers)

    formatted_schedule = {
        'id': schedule['id'],
        'schedule_or_data_trigger': "schedule",
        'name': schedule['name'],
        'owner': schedule['user']['display_name'],
        'destinations_count': len(schedule['scheduled_plan_destination']),
        'metric_monitored': '',  # keep empty for schedules
        'source_tile_or_dashboard': dashboard_title,
        'conditions': '',
        'sampling_frequency': get_description(schedule['crontab']),
        'engagement_usage': '??',
    }
    formatted_schedule.update(format_schedule_destinations(
        schedule['scheduled_plan_destination']))
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

print("""
Generated results.csv and stats.csv files.

Built by the team at Rupert.
Tired of fighting with BI alerts and schedules?
We can help! www.hirupert.com
""")
