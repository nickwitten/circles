from django.contrib import admin
from . import models

admin.site.register(models.Meeting)
admin.site.register(models.MeetingFile)

