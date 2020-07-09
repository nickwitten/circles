import os

from django.db import models
from django.forms import model_to_dict

import members.models as members_models
from circles import settings


class Programming(models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='programming')
    title = models.CharField(max_length=128)
    length = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)
    facilitators = models.TextField(default='[]', blank=True)
    facilitator_profiles = models.ManyToManyField(members_models.Profile,
                                                  related_name='facilitate_programming', blank=True)
    links = models.TextField(default='[]', blank=True)

    def to_dict(self):
        model_info = model_to_dict(self)
        model_info['facilitator_profiles'] = [[str(profile), profile.pk] for profile in
                                              model_info['facilitator_profiles']]
        return model_info


class Theme(models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='themes')
    title = models.CharField(max_length=128)
    required_for = models.TextField(blank=True)

    def to_dict(self):
        return model_to_dict(self)


class ProfileTheme(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='profiles')
    profile = models.ForeignKey(members_models.Profile, on_delete=models.CASCADE, related_name='themes')
    date_completed = models.DateField(blank=True, null=True)


class Module(models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='modules')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='modules')
    required_for = models.TextField(default='[]', blank=True)
    facilitator_profiles = models.ManyToManyField(members_models.Profile,
                                                  blank=True, related_name='facilitate_modules')
    title = models.CharField(max_length=128)
    length = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)
    facilitators = models.TextField(default='[]', blank=True)
    links = models.TextField(default='[]', blank=True)

    def to_dict(self):
        model_info = model_to_dict(self)
        model_info['facilitator_profiles'] = [[str(profile), profile.pk] for profile in
                                              model_info['facilitator_profiles']]
        return model_info


class ProfileModule(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='profiles')
    profile = models.ForeignKey(members_models.Profile, on_delete=models.CASCADE, related_name='modules')
    date_completed = models.DateField(blank=True, null=True)


class ProgrammingFile(models.Model):
    model = models.ForeignKey(Programming, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='learning_files/')
    title = models.CharField(max_length=128)

    def delete_file(self):
        try:
            os.remove('/'.join([settings.MEDIA_ROOT, self.file.name]))
        except:
            print('file not deleted at', '/'.join([settings.MEDIA_ROOT, self.file.name]))


class ModuleFile(models.Model):
    model = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='learning_files/')
    title = models.CharField(max_length=128)

    def delete_file(self):
        try:
            os.remove('/'.join([settings.MEDIA_ROOT, self.file.name]))
        except:
            print('file not deleted at', '/'.join([settings.MEDIA_ROOT, self.file.name]))
