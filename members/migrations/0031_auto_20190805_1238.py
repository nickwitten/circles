# Generated by Django 2.2.2 on 2019-08-05 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0030_auto_20190805_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='child',
            name='allergies',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='child',
            name='dietary_modifications',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='child',
            name='disabilities',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='child',
            name='medications',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='child',
            name='physical_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
