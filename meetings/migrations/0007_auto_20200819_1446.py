# Generated by Django 2.2.2 on 2020-08-19 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0003_auto_20200804_1312'),
        ('members', '0001_initial'),
        ('meetings', '0006_auto_20200816_2039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meeting',
            name='attendees_objects',
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='lists_objects',
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='modules_objects',
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='programming_objects',
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='attendees',
        ),
        migrations.AddField(
            model_name='meeting',
            name='attendees',
            field=models.ManyToManyField(blank=True, to='members.Profile'),
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='lists',
        ),
        migrations.AddField(
            model_name='meeting',
            name='lists',
            field=models.ManyToManyField(blank=True, to='members.FilterSet'),
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='modules',
        ),
        migrations.AddField(
            model_name='meeting',
            name='modules',
            field=models.ManyToManyField(blank=True, related_name='modules', to='learning.Module'),
        ),
        migrations.RemoveField(
            model_name='meeting',
            name='programming',
        ),
        migrations.AddField(
            model_name='meeting',
            name='programming',
            field=models.ManyToManyField(blank=True, related_name='programming', to='learning.Programming'),
        ),
    ]