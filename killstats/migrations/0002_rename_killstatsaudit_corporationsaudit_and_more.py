# Generated by Django 4.2.11 on 2024-08-15 11:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eveonline", "0017_alliance_and_corp_names_are_not_unique"),
        ("killstats", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="KillstatsAudit",
            new_name="CorporationsAudit",
        ),
        migrations.CreateModel(
            name="AlliancesAudit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("last_update", models.DateTimeField(auto_now=True)),
                (
                    "alliance",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="eveonline.eveallianceinfo",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="eveonline.evecharacter",
                    ),
                ),
            ],
            options={
                "default_permissions": (),
            },
        ),
    ]
