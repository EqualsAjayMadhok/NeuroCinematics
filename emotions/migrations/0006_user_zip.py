# Generated by Django 5.0.1 on 2024-01-14 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("emotions", "0005_visualization_register"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="zip",
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
