# Generated by Django 4.2.16 on 2024-10-19 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_people_educations'),
    ]

    operations = [
        migrations.AddField(
            model_name='people',
            name='middle_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
