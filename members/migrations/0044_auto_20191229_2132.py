# Generated by Django 2.2.2 on 2019-12-30 02:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0043_auto_20191229_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='site',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
