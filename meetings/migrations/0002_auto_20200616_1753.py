# Generated by Django 2.2.2 on 2020-06-16 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='links',
            field=models.CharField(default='[]', max_length=1024),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='meeting',
            name='notes',
            field=models.TextField(blank=True, max_length=2048),
        ),
    ]