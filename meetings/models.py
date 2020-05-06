from django.db import models

class Meeting(models.Model):
    title = models.CharField(max_length=64)
    start_time = models.DateTimeField(verbose_name="Start Time")
    end_time = models.DateTimeField(verbose_name="End Time")

    def __str__(self):
        return f'{self.title}'
