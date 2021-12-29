# Generated by Django 2.2 on 2021-12-29 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_auto_20211229_1508'),
        ('meetings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='non_attendees',
            field=models.ManyToManyField(blank=True, related_name='unattended_meetings', to='members.Profile'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='attendees',
            field=models.ManyToManyField(blank=True, related_name='attended_meetings', to='members.Profile'),
        ),
    ]