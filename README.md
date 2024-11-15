# Killstats module for AllianceAuth.<a name="aa-killstats"></a>

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Geuthur/aa-killstats/master.svg)](https://results.pre-commit.ci/latest/github/Geuthur/aa-killstats/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/Geuthur/aa-killstats/actions/workflows/autotester.yml/badge.svg)](https://github.com/Geuthur/aa-killstats/actions/workflows/autotester.yml)
[![codecov](https://codecov.io/gh/Geuthur/aa-killstats/graph/badge.svg?token=jRicu5enZF)](https://codecov.io/gh/Geuthur/aa-killstats)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/W7W810Q5J4)

Killstats for Corporations & Alliances, Hall of Fame, Hall of Shame, etc.

## -

- [AA Killstats](#aa-killstats)
  - [Features](#features)
  - [Upcoming](#upcoming)
  - [Installation](#features)
    - [Step 0 - Check dependencies are installed](#step0)
    - [Step 1 - Install the Package](#step1)
    - [Step 2 - Configure Alliance Auth](#step2)
    - [Step 3 - Add the Scheduled Tasks and Settings](#step3)
    - [Step 4 - Migration to AA](#step4)
    - [Step 5 - Setting up Permissions](#step5)
    - [Step 6 - (Optional) Setting up Compatibilies](#step6)
  - [Highlights](#highlights)

## Features<a name="features"></a>

- Graphical Overview
- Corporation & Alliance Overview
- Kills/Losses
- Main Character and Alts combined ([explanation](/killstats/docs/explanation.md))
- Hall of Fame, Hall of Shame
- Killstats like Top Kill, Top Killer, Top Loss, Alltime Killer, etc.
- Top 10 list for each Month

## Upcoming<a name="upcoming"></a>

- Filtering Settings for each Corporation / Alliance
- Administration Access for specific Corps or Alliances

## Installation<a name="installation"></a>

> \[!NOTE\]
> AA Killstats needs at least Alliance Auth v4.0.0
> Please make sure to update your Alliance Auth before you install this APP

### Step 0 - Check dependencies are installed<a name="step0"></a>

- Ledger needs the app [django-eveuniverse](https://apps.allianceauth.org/apps/detail/django-eveuniverse) to function. Please make sure it is installed.

### Step 1 - Install the Package<a name="step1"></a>

Make sure you're in your virtual environment (venv) of your Alliance Auth then install the pakage.

```shell
pip install aa-killstats
```

### Step 2 - Configure Alliance Auth<a name="step2"></a>

Configure your Alliance Auth settings (`local.py`) as follows:

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

| ID             | Description                     |                                                                  |
| :------------- | :------------------------------ | :--------------------------------------------------------------- |
| `basic_access` | Can access this app, Killstats. | All Members with the Permission can access the Killstats App.    |
| `admin_access` | Has access to all killstats.    | Has access to all Killstats Views, Can add Corporation/Alliance. |

### Step 6 - (Optional) Setting up Compatibilies<a name="step6"></a>

The Following Settings can be setting up in the `local.py`

- KILLSTATS_APP_NAME:          `"YOURNAME"`     - Set the name of the APP

- KILLSTATS_LOGGER_USE:        `True / False`   - Set to use own Logger File

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

![Stats](/killstats/docs/img/killstats1.png)
![Hall](/killstats/docs/img/killstats2.png)
![Kills](/killstats/docs/img/killstats3.png)

> \[!NOTE\]
> Contributing
> You want to improve the project?
> Just Make a [Pull Request](https://github.com/Geuthur/aa-killstats/pulls) with the Guidelines.
> We Using pre-commit
