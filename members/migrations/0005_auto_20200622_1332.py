# Generated by Django 2.2.2 on 2020-06-22 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_auto_20200620_2310'),
    ]

    operations = [
        migrations.RenameField(
            model_name='child',
            old_name='physical_date',
            new_name='date_of_last_physical_exam',
        ),
        migrations.RenameField(
            model_name='child',
            old_name='health_issues',
            new_name='known_health_issues',
        ),
    ]
