# Killstats module for AllianceAuth.<a name="aa-killstats"></a>

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Geuthur/aa-killstats/master.svg)](https://results.pre-commit.ci/latest/github/Geuthur/aa-killstats/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/Geuthur/aa-killstats/actions/workflows/autotester.yml/badge.svg)](https://github.com/Geuthur/aa-killstats/actions/workflows/autotester.yml)
[![codecov](https://codecov.io/gh/Geuthur/aa-killstats/graph/badge.svg?token=jRicu5enZF)](https://codecov.io/gh/Geuthur/aa-killstats)

- [AA Killstats](#aa-killstats)
  - [Features](#features)
  - [Upcoming](#upcoming)
  - [Installation](#features)
    - [Step 1 - Install the Package](#step1)
    - [Step 2 - Configure Alliance Auth](#step2)
    - [Step 3 - Add the Scheduled Tasks and Settings](#step3)
    - [Step 4 - Migration to AA](#step4)
    - [Step 5 - Setting up Permissions](#step5)
    - [Step 6 - (Optional) Setting up Compatibilies](#step6)
  - [Highlights](#highlights)

## Features<a name="features"></a>

- Graphical Overview
- Kills from alts count to Main Character
- Hall of Fame, Hall of Shame
- Killstats like Top Kill, Top Killer, Top Loss, Alltime Killer, etc.
- Kills/Losses

## Upcoming<a name="upcoming"></a>

- Access to Killboards from other Corporation (Admin Access)

## Installation<a name="installation"></a>

> \[!NOTE\]
> AA Killstats needs at least Alliance Auth v4.0.0
> Please make sure to update your Alliance Auth before you install this APP

### Step 1 - Install the Package<a name="step1"></a>

Make sure you're in your virtual environment (venv) of your Alliance Auth then install the pakage.

```shell
pip install aa-killstats
```

### Step 2 - Configure Alliance Auth<a name="step2"></a>

Configure your Alliance Auth settings (`local.py`) as follows:

- Add `'allianceauth.corputils',` to `INSTALLED_APPS`
- Add `'eveuniverse',` to `INSTALLED_APPS`
- Add `'killstats',` to `INSTALLED_APPS`

### Step 3 - Add the Scheduled Tasks<a name="step3"></a>

To set up the Scheduled Tasks add following code to your `local.py`

```python
CELERYBEAT_SCHEDULE["killstats_killmail_fetch"] = {
    "task": "killstats.tasks.killmail_fetch_all",
    "schedule": crontab(minute=0, hour="*/1"),
}
```

### Step 4 - Migration to AA<a name="step4"></a>

```shell
python manage.py collectstatic
python manage.py migrate
```

### Step 5 - Setting up Permissions<a name="step5"></a>

With the Following IDs you can set up the permissions for the KILLSTATS

| ID             | Description                       |                                                               |
| :------------- | :-------------------------------- | :------------------------------------------------------------ |
| `basic_access` | Can access the Killstats module   | All Members with the Permission can access the Killstats App. |
| `admin_access` | Can Add Corporations to Killstats | Can Add Corporations to Killstats                             |

### Step 6 - (Optional) Setting up Compatibilies<a name="step6"></a>

The Following Settings can be setting up in the `local.py`

- KILLSTATS_APP_NAME:          `"YOURNAME"`     - Set the name of the APP

- KILLSTATS_LOGGER_USE:        `True / False`   - Set to use own Logger File

- KILLSTATS_CORPSTATS_TWO:     `True / False`   - Set to use Corp Stats Two APP to Fetch Members that are not registred

If you set up KILLSTATS_LOGGER_USE to `True` you need to add the following code below:

```python
LOGGING_KILLSTATS = {
    "handlers": {
        "killstats_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "log/killstats.log"),
            "formatter": "verbose",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
        },
    },
    "loggers": {
        "killstats": {
            "handlers": ["killstats_file", "console"],
            "level": "INFO",
        },
    },
}
LOGGING["handlers"].update(LOGGING_KILLSTATS["handlers"])
LOGGING["loggers"].update(LOGGING_KILLSTATS["loggers"])
```

## Highlights<a name="highlights"></a>

![Screenshot 2024-06-26 144010](https://github.com/Geuthur/aa-killstats/assets/761682/edc23d4d-719a-4519-b96a-ffbb950d28ca)

> \[!NOTE\]
> Contributing
> You want to improve the project?
> Just Make a [Pull Request](https://github.com/Geuthur/aa-killstats/pulls) with the Guidelines.
> We Using pre-commit
