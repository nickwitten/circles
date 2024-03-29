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

    def get_attached_models(self, klass, pks):
        if klass == members_models.Profile:
            # Check that profile is in same site as model when adding
            profiles = klass.objects.filter(pk__in=pks)
            profiles = profiles.filter(pk__in=self.site.profiles().values_list('pk'))
            return profiles
        else:
            super().get_attached_models(klass, pks)


class ProgrammingFile(models.Model):
    model = models.ForeignKey(Programming, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='program_files/')
    title = models.CharField(max_length=128)

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
        self.update_profile_connections()

    def update_profile_connections(self):
        required_positions = json.loads(self.required_for)
        profiles = self.site.profiles().filter(roles__position__in=required_positions)
        # Add to profiles with required position
        for profile in profiles:
            if not self.profiles.filter(profile=profile):
                ProfileTheme.objects.create(theme=self, profile=profile)
        # Remove from profiles without required position and not completed
        for profile_theme in self.profiles.exclude(profile__in=profiles):
            if not profile_theme.end_date:
                profile_theme.delete()

    def order_open_modules(self, profile):
        modules = ProfileModule.objects.filter(profile=profile, module__theme=self).order_by('module__title')
        complete = modules.filter(end_date__isnull=False)
        incomplete = modules.filter(end_date__isnull=True)
        return complete | incomplete

    def create_profile_connection(self, profile):
        ProfileTheme.objects.create(theme=self, profile=profile)



class ProfileTheme(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='profiles')
    profile = models.ForeignKey(members_models.Profile, on_delete=models.CASCADE, related_name='themes')
    end_date = models.DateField(blank=True, null=True)

    @staticmethod
    def get_related(profile):
        trainings = ProfileTheme.objects.filter(profile=profile).order_by('theme__title')
        return trainings
        # pks = [theme.pk for theme in trainings['sites']]

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
            self.update_theme_required_for()
        self.update_profile_connections()

    def update_profile_connections(self):
        required_positions = json.loads(self.required_for)
        profiles = self.site.profiles().filter(roles__position__in=required_positions)
        # Add to profiles with required position
        for profile in profiles:
            if not self.profiles.filter(profile=profile):
                ProfileModule.objects.create(module=self, profile=profile)
        # Remove from profiles without required position and not completed
        for profile_module in self.profiles.exclude(profile__in=profiles):
            if not profile_module.end_date:
                profile_module.delete()

    def update_theme_required_for(self):
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

    def create_profile_connection(self, profile):
        ProfileModule.objects.create(module=self, profile=profile)


class ProfileModule(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='profiles')
    profile = models.ForeignKey(members_models.Profile, on_delete=models.CASCADE, related_name='modules')
    end_date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        check_remove = kwargs.pop('theme_remove', False)
        super().save(*args, **kwargs)
        self.update_theme_completion(check_remove=check_remove)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_theme_completion(check_remove=True)

    def update_theme_completion(self, check_remove=False):
        all_completed = True
        for module in self.module.theme.modules.all():
            profile_module = module.profiles.filter(profile=self.profile).first()
            if not profile_module or not profile_module.end_date:
                all_completed = False
        theme_profile = self.module.theme.profiles.filter(profile=self.profile).first()
        if all_completed:
            self.profile.add_learning(self.module.theme, ProfileTheme, self.end_date)
        elif check_remove and theme_profile and theme_profile.end_date:
            theme_profile.end_date = None
            theme_profile.save()

    @staticmethod
    def get_related(profile):
        trainings = ProfileModule.objects.filter(profile=profile).order_by('module__title')
        return trainings


class ModuleFile(models.Model):
    model = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='training_files/')
    title = models.CharField(max_length=128)

