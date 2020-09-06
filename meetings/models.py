import json

from django.db import models

from members.models import Profile, FilterSet, Site
import os
from circles import settings
from dashboard.models import FileFieldMixin, DictMixin
import learning.models as learning_models

class Meeting(FileFieldMixin, DictMixin, models.Model):
    type = models.CharField(max_length=64)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='meetings',
                             null=True)
    programming = models.ManyToManyField(learning_models.Programming,
                                                 blank=True, related_name='programming')
    modules = models.ManyToManyField(learning_models.Module,
                                            blank=True, related_name='modules')
    modules_to_attendees = models.TextField(default='{}')
    location = models.CharField(max_length=128, blank=True)
    start_time = models.DateTimeField(verbose_name="Start Time", )
    end_time = models.DateTimeField(verbose_name="End Time")
    lists = models.ManyToManyField(FilterSet, blank=True)
    attendees = models.ManyToManyField(Profile, blank=True)
    color = models.CharField(max_length=32)
    notes = models.TextField(blank=True)
    links = models.TextField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FileModelClass = MeetingFile

    def __str__(self):
        return f'{self.site} - {self.type}'

    def train_members(self):
        for module_pk, attendees in json.loads(self.modules_to_attendees).items():
            module = self.modules.filter(pk=module_pk).first()
            if not module:
                continue
            attendees = self.attendees.all() if attendees == 'all' else self.attendees.filter(pk__in=attendees)
            for attendee in attendees:
                attendee.add_learning(module, learning_models.ProfileModule, self.start_time.strftime('%Y-%m-%d'))


class MeetingFile(models.Model):
    model = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='meeting_files/')
    title = models.CharField(max_length=128)

    def delete_file(self):
        try:
            os.remove('/'.join([settings.MEDIA_ROOT, self.file.name]))
        except:
            print('file not deleted at', '/'.join([settings.MEDIA_ROOT, self.file.name]))
