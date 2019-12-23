# Generated by Django 2.2.2 on 2019-08-05 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0035_child_child_info'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='child',
            name='profile',
        ),
        migrations.AddField(
            model_name='childinfo',
            name='profile',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='members.Profile'),
            preserve_default=False,
        ),
    ]
