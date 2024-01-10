# Looker Alerts & Schedules Extraction Utility
A simple python utility for downloading details of all the alerts or schedules configured in your Looker instance.

Built by the team at Rupert. Tired of struggling with BI alerts and schedules? [We can help!](https://www.hirupert.com)

## What does the utility do?
It generates a csv file containing all the alerts and schedules found in your Looker instance. Point the utility at your Looker instance, pass it API credentials and you'll get a file that looks like this:

_screenshot_

### Why?
Managing contnet in Looker is hard. Most instances are cluttered. Alerts and schedules serve a crucual data distribution function. This utility makes it easy to review and understand 

## Getting Started
We use `pipenv` to manage our dependencies. To install the dependencies, run:

```bash
pipenv install
```

To run the script, run:

```bash
pipenv run python3 main.py
```

Environment variables are used to configure the script. The following environment variables are used:
- `LOOKER_API_BASE_URL`: The base URL of the Looker API. This is usually `https://<instance_name>.cloud.looker.com`.
- `LOOKER_CLIENT_ID`: The API client ID to use for the Looker instance.
- `LOOKER_CLIENT_SECRET`: The API client secret to use for the Looker instance.

If one or more of these environment variables are not set, the script will prompt you to enter them.

### Optional: Run the script with Replit
