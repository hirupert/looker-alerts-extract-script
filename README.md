# Looker Alerts & Schedules Extraction Utility
A simple python utility for downloading details of all the alerts or schedules configured in your Looker instance.

Built by the team at Rupert. Tired of fighting with clunky BI alerts and schedules? [We can help!](https://www.hirupert.com)

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
