# Generated by Django 4.2.16 on 2024-10-21 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_people_school_action_id_post_commented_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]