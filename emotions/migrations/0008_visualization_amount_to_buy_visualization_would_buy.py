# Generated by Django 5.0.1 on 2024-01-15 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("emotions", "0007_register_emotionintensity"),
    ]

    operations = [
        migrations.AddField(
            model_name="visualization",
            name="amount_to_buy",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="visualization",
            name="would_buy",
            field=models.BooleanField(default=False),
        ),
    ]
