# Generated by Django 5.0.1 on 2024-01-14 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("emotions", "0006_user_zip"),
    ]

    operations = [
        migrations.AddField(
            model_name="register",
            name="emotionIntensity",
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
