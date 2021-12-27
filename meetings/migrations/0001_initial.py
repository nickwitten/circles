# Generated by Django 2.2 on 2021-12-27 18:43

import dashboard.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('members', '0001_initial'),
        ('learning', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=64)),
                ('modules_to_attendees', models.TextField(default='{}')),
                ('location', models.CharField(blank=True, max_length=128)),
                ('start_time', models.DateTimeField(verbose_name='Start Time')),
                ('end_time', models.DateTimeField(verbose_name='End Time')),
                ('color', models.CharField(max_length=32)),
                ('notes', models.TextField(blank=True)),
                ('links', models.TextField()),
                ('attendees', models.ManyToManyField(blank=True, to='members.Profile')),
                ('lists', models.ManyToManyField(blank=True, to='members.FilterSet')),
                ('modules', models.ManyToManyField(blank=True, related_name='meetings', to='learning.Module')),
                ('programming', models.ManyToManyField(blank=True, related_name='meetings', to='learning.Programming')),
                ('site', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='members.Site')),
            ],
            bases=(dashboard.models.FileFieldMixin, dashboard.models.DictMixin, models.Model),
        ),
        migrations.CreateModel(
            name='MeetingFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='meeting_files/')),
                ('title', models.CharField(max_length=128)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='meetings.Meeting')),
            ],
        ),
    ]
