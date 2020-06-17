from django.db import models
from members.models import Profile, FilterSet, Site
import os
from circles import settings

class Meeting(models.Model):
    type = models.CharField(max_length=64)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='meetings', null=True)
    location = models.CharField(max_length=128, blank=True)
    start_time = models.DateTimeField(verbose_name="Start Time", )
    end_time = models.DateTimeField(verbose_name="End Time")
    attendance_lists = models.ManyToManyField(FilterSet, blank=True)
    attendees = models.ManyToManyField(Profile, blank=True)
    color = models.CharField(max_length=32)
    notes = models.TextField(max_length=2048, blank=True)
    links = models.CharField(max_length=1024)

    def __str__(self):
        return f'{self.site} - {self.type}'


class MeetingFile(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='meeting_files/')
    title = models.CharField(max_length=128)

    def delete_file(self):
        try:
            os.remove('/'.join([settings.MEDIA_ROOT, self.file.name]))
        except:
            print('file not deleted at', '/'.join([settings.MEDIA_ROOT, self.file.name]))
