# Generated by Django 2.2.2 on 2020-09-06 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0007_auto_20200819_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='modules_to_attendees',
            field=models.TextField(default='{}'),
        ),
    ]
