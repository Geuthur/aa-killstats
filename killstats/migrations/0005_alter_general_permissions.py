# Django
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "killstats",
            "0004_alter_attacker_corporation_alter_eveentity_alliance_and_more",
        ),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="general",
            options={
                "default_permissions": (),
                "managed": False,
                "permissions": [
                    ("basic_access", "Can access this app, Killstats."),
                    ("admin_access", "Has access to all killstats."),
                ],
                "verbose_name": "AA-Killstats",
                "verbose_name_plural": "AA-Killstats",
            },
        ),
    ]
