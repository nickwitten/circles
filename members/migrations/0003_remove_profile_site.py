# Generated by Django 2.2.2 on 2020-06-19 17:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0002_profile_site'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='site',
        ),
    ]