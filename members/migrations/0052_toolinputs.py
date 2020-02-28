# Generated by Django 2.2.2 on 2020-02-12 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0051_auto_20200202_2359'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToolInputs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('searchinput', models.CharField(blank=True, max_length=16, null=True)),
                ('filterby', models.CharField(blank=True, max_length=16, null=True)),
                ('filterinput', models.CharField(blank=True, max_length=16, null=True)),
                ('sortby', models.CharField(blank=True, max_length=16, null=True)),
                ('data', models.CharField(blank=True, max_length=16, null=True)),
            ],
        ),
    ]