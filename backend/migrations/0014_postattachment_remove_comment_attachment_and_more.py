# Generated by Django 4.2.16 on 2024-10-23 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_people_is_deactivated_post_mentions'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ppst_owner', models.CharField(blank=True, default='', max_length=255)),
                ('post_id', models.CharField(blank=True, default='', max_length=255)),
                ('attachment', models.FileField(blank=True, default='', null=True, upload_to='uploads/')),
            ],
        ),
        migrations.RemoveField(
            model_name='comment',
            name='attachment',
        ),
        migrations.RemoveField(
            model_name='post',
            name='content_file',
        ),
        migrations.RemoveField(
            model_name='post',
            name='title',
        ),
        migrations.AddField(
            model_name='cotform',
            name='cot_form_id',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='ipcrfform',
            name='connection_to_other',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='rpmsfolder',
            name='is_for_teacher_proficient',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rpmsfolder',
            name='rpms_folder_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='rpmsfolder',
            name='rpms_folder_school_year',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
