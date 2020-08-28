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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for module in self.modules.all():
            for attendee in self.attendees.all():
                print("add " + str(module) + " training to " + str(attendee))


class MeetingFile(models.Model):
    model = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='meeting_files/')
    title = models.CharField(max_length=128)

    def delete_file(self):
        try:
            os.remove('/'.join([settings.MEDIA_ROOT, self.file.name]))
        except:
            print('file not deleted at', '/'.join([settings.MEDIA_ROOT, self.file.name]))
