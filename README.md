
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
- `LOOKER_API_TOKEN`: The API token to use for the Looker instance.

How to generate API token: https://cloud.google.com/looker/docs/api-auth
