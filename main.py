import os
import requests
import csv
from urllib.parse import urljoin

api_url = urljoin(os.environ.get('LOOKER_API_BASE_URL'), "api/")
api_client_id = os.environ.get('LOOKER_CLIENT_ID')
api_client_secret = os.environ.get('LOOKER_CLIENT_SECRET')

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

# TODO figure out how to flatten lists such as destinations and scheduled_plan_destination

fieldnames = ['type'] + list(fields_alerts) + list(fields_schedules)
fieldnames = list(set(fieldnames))  # remove duplicates

result_file = open('results.csv', 'w')
writer = csv.DictWriter(result_file, fieldnames=fieldnames)
writer.writeheader()

for alert in alerts:
    alert['type'] = 'alert'
    writer.writerow(alert)
for schedule in schedules:
    schedule['type'] = 'schedule'
    writer.writerow(schedule)

result_file.close()
