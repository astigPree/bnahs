# Generated by Django 4.2.16 on 2024-10-21 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_mainadmin_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotform',
            name='is_checked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ipcrfform',
            name='is_checked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rpmsattachment',
            name='is_checked',
            field=models.BooleanField(default=False),
        ),
    ]
