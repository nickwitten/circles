from django.db import models
from members.models import Profile, FilterSet

class Meeting(models.Model):
    title = models.CharField(max_length=64)
    start_time = models.DateTimeField(verbose_name="Start Time", )
    end_time = models.DateTimeField(verbose_name="End Time")
    attendance_lists = models.ManyToManyField(FilterSet, blank=True)
    attendees = models.ManyToManyField(Profile, blank=True)
    color = models.CharField(max_length=32)

    def __str__(self):
        return f'{self.title}'
