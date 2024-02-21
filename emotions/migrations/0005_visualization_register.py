# Generated by Django 5.0.1 on 2024-01-08 22:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("emotions", "0004_remove_user_last_login"),
    ]

    operations = [
        migrations.CreateModel(
            name="Visualization",
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
                ("confirmed", models.BooleanField(default=False)),
                ("video_id", models.IntegerField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="emotions.user"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Register",
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
                ("playback_timestamp", models.FloatField()),
                ("dominantEmotion", models.CharField(max_length=50)),
                ("attention", models.FloatField()),
                (
                    "visualization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="emotions.visualization",
                    ),
                ),
            ],
        ),
    ]
