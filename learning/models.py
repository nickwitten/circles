import json
import os
from datetime import datetime

from django.db import models
from django.forms import model_to_dict

import members.models as members_models
from circles import settings

from dashboard.models import JsonM2MFieldModelMixin, FileFieldMixin, DictMixin

class Programming(FileFieldMixin, JsonM2MFieldModelMixin, DictMixin, models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='programming')
    title = models.CharField(max_length=128)
    length = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)
    facilitators = models.TextField(default='[]', blank=True)
    facilitators_objects = models.ManyToManyField(members_models.Profile,
                                                  related_name='facilitate_programming', blank=True)
    links = models.TextField(default='[]', blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.JsonM2MFields = [['facilitators', members_models.Profile]]
        self.FileModelClass = ProgrammingFile

    def __str__(self):
        return f'{self.title}'

    def get_attached_models(self, klass, items):
        pks = [item['pk'] for item in items]
        if klass == members_models.Profile:
            # Check that profile is in same site as model when adding
            profiles = klass.objects.filter(pk__in=pks)
            profiles = profiles.filter(pk__in=self.site.profiles().values_list('pk'))
            return profiles
        else:
            super().get_attached_models(klass, pks)


class ProgrammingFile(models.Model):
    model = models.ForeignKey(Programming, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='learning_files/')
    title = models.CharField(max_length=128)

    def delete_file(self):
        try:
            os.remove('/'.join([settings.MEDIA_ROOT, self.file.name]))
        except:
            print('file not deleted at', '/'.join([settings.MEDIA_ROOT, self.file.name]))


class Theme(DictMixin, models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='themes')
    title = models.CharField(max_length=128)
    required_for = models.TextField(default='[]', blank=True)

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        kwargs.pop('files', None)
        required_checked = kwargs.pop('required_checked', None)
        super().save(*args, **kwargs)
        if not required_checked:
            # Apply required for to all containing modules
            required_for = json.loads(self.required_for)
            for module in self.modules.all():
                module_required_for = json.loads(module.required_for)
                module_required_for = list(set(module_required_for + required_for))
                module.required_for = json.dumps(module_required_for)
                module.save(required_checked=True)


class ProfileTheme(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='profiles')
    profile = models.ForeignKey(members_models.Profile, on_delete=models.CASCADE, related_name='themes')
    date_completed = models.DateField(blank=True, null=True)


class Module(FileFieldMixin, JsonM2MFieldModelMixin, DictMixin, models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='modules')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='modules')
    required_for = models.TextField(default='[]', blank=True)
    title = models.CharField(max_length=128)
    length = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)
    facilitators = models.TextField(default='[]', blank=True)
    facilitators_objects = models.ManyToManyField(members_models.Profile,
                                                  blank=True, related_name='facilitate_modules')
    links = models.TextField(default='[]', blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.JsonM2MFields = [['facilitators', members_models.Profile]]
        self.FileModelClass = ModuleFile

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        required_checked = kwargs.pop('required_checked', None)
        super().save(*args, **kwargs)
        if not required_checked:
            # Overwrite themes required_for if this doesn't include it
            module_required_for = json.loads(self.required_for)
            theme_required_for = json.loads(self.theme.required_for)
            theme_required_for = [position for position in theme_required_for
                                  if position in module_required_for]
            self.theme.required_for = json.dumps(theme_required_for)
            self.theme.save(required_checked=True)

    def get_attached_models(self, klass, pks):
        if klass == members_models.Profile:
            # Check that profile is in same site as model when adding
            profiles = klass.objects.filter(pk__in=pks)
            profiles = profiles.filter(pk__in=self.site.profiles().values_list('pk'))
            return profiles
        else:
            super().get_attached_models(klass, pks)


class ProfileModule(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='profiles')
    profile = models.ForeignKey(members_models.Profile, on_delete=models.CASCADE, related_name='modules')
    date_completed = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_theme_completion()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_theme_completion()

    def update_theme_completion(self):
        all_completed = True
        for module in self.module.theme.modules.all():
            profile_module = module.profiles.filter(profile=self.profile).first()
            if not profile_module or not profile_module.date_completed:
                all_completed = False
        # theme_profile = self.module.theme.profiles.filter(profile=self.profile).first()
        if all_completed:
            self.profile.add_learning(self.module.theme, ProfileTheme, self.date_completed)
        # This removes theme completion.  If more modules were added to theme,
        # profiles would lose theme completion on save
        # elif theme_profile and theme_profile.date_completed:
        #     theme_profile.date_completed = None
        #     theme_profile.save()


class ModuleFile(models.Model):
    model = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='learning_files/')
    title = models.CharField(max_length=128)

    def delete_file(self):
        try:
            os.remove('/'.join([settings.MEDIA_ROOT, self.file.name]))
        except:
            print('file not deleted at', '/'.join([settings.MEDIA_ROOT, self.file.name]))
