# Generated by Django 2.2.2 on 2020-02-14 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0057_auto_20200213_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toolinputs',
            name='filters',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
    ]