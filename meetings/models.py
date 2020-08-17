from itertools import chain

from django.db import models
from members.models import Profile, FilterSet, Site
import os
from circles import settings
from dashboard.models import FileFieldMixin, JsonM2MFieldModelMixin
import learning.models as learning_models
import members.models as members_models

class Meeting(FileFieldMixin ,JsonM2MFieldModelMixin, models.Model):
    type = models.CharField(max_length=64)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='meetings',
                             null=True)
    programming = models.TextField(default='[]', blank=True)
    programming_objects = models.ManyToManyField(learning_models.Programming,
                                                 blank=True, related_name='programming')
    modules = models.TextField(default='[]', blank=True)
    modules_objects = models.ManyToManyField(learning_models.Module,
                                            blank=True, related_name='modules')
    location = models.CharField(max_length=128, blank=True)
    start_time = models.DateTimeField(verbose_name="Start Time", )
    end_time = models.DateTimeField(verbose_name="End Time")
    lists = models.TextField(default='[]', blank=True)
    lists_objects = models.ManyToManyField(FilterSet, blank=True)
    attendees = models.TextField(default='[]', blank=True)
    attendees_objects = models.ManyToManyField(Profile, blank=True)
    color = models.CharField(max_length=32)
    notes = models.TextField(blank=True)
    links = models.TextField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.JsonM2MFields = [['programming', learning_models.Programming],
                              ['modules', learning_models.Module],
                              ['lists', members_models.FilterSet],
                              ['attendees', members_models.Profile]]
        self.FileModelClass = MeetingFile

    def __str__(self):
        return f'{self.site} - {self.type}'


class MeetingFile(models.Model):
    model = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='meeting_files/')
    title = models.CharField(max_length=128)

    def delete_file(self):
        try:
            os.remove('/'.join([settings.MEDIA_ROOT, self.file.name]))
        except:
            print('file not deleted at', '/'.join([settings.MEDIA_ROOT, self.file.name]))
