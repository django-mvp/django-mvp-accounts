"""Create the table that holds the names people give their API tokens.

Written by hand. Django's migration writer reads a ``KNOX_TOKEN_MODEL`` setting
to place a table that points at knox's token model, and a project that uses
knox's own model never defines it. knox's settings always know the model.
"""

import django.db.models.deletion
from django.db import migrations, models
from knox.settings import knox_settings


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        (knox_settings.TOKEN_MODEL.split(".")[0], "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="TokenName",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="What the token is for, so you can recognise it later.",
                        max_length=64,
                        verbose_name="name",
                    ),
                ),
                (
                    "token",
                    models.OneToOneField(
                        help_text="The API token this name belongs to.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mvp_accounts_name",
                        swappable=False,
                        to=knox_settings.TOKEN_MODEL,
                        verbose_name="token",
                    ),
                ),
            ],
            options={
                "verbose_name": "API token name",
                "verbose_name_plural": "API token names",
            },
        ),
    ]
