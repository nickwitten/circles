from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Profile)
admin.site.register(models.Site)
admin.site.register(models.Chapter)
admin.site.register(models.Residence)
admin.site.register(models.Role)
admin.site.register(models.Child)
admin.site.register(models.ChildInfo)
admin.site.register(models.FilterSet)
