# Generated by Django 4.2.16 on 2024-11-09 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0024_cotform_school_year"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotform",
            name="quarter",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
