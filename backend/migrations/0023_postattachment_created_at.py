# Generated by Django 4.2.16 on 2024-11-03 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0022_people_created_at_alter_comment_created_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="postattachment",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
