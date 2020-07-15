from django.contrib import admin
from learning import models

# Register your models here.

admin.site.register(models.Programming)
admin.site.register(models.Theme)
admin.site.register(models.Module)
admin.site.register(models.ProgrammingFile)
admin.site.register(models.ModuleFile)
admin.site.register(models.ProfileTheme)
admin.site.register(models.ProfileModule)
