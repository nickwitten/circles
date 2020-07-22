import json
import os

from django.db import models
from django.forms import model_to_dict

import members.models as members_models
from circles import settings


class JsonM2MFieldModelMixin:
    JsonM2MFields = []

    def save(self, *args, **kwargs):
        """ Removes dicts from json field and adds those
            objects to manytomany relationship.  Dicts
            must contain pk key to be added to model    """
        model = super().save(*args, **kwargs)
        for i, field in enumerate(self.JsonM2MFields):
            # Grab and remove dicts from json string
            try:
                field_value = json.loads(getattr(self, field[0]))
            except Exception as e:
                field_value = None
            if field_value:
                pks = []
                for item in field_value:
                    if 'pk' in item:
                        pks.append(item['pk'])
                self.JsonM2MFields[i].append(pks)
            else:
                self.JsonM2MFields[i].append([])
        # add objects with those pks to model
        for field in self.JsonM2MFields:
            attached_models = self.get_attached_models(field)
            objects_field = getattr(self, field[0] + '_objects')
            objects_field.clear()
            objects_field.add(*attached_models)
        return model

    @staticmethod
    def get_attached_models(field):
        attached_models = field[1].objects.filter(pk__in=field[2])
        field.pop(2)
        return attached_models

    def to_dict(self):
        model_info = model_to_dict(self)
        for field in self.JsonM2MFields:
            model_info.pop(field[0]+'_objects')
        return model_info


class Programming(JsonM2MFieldModelMixin, models.Model):
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

    def __str__(self):
        return f'{self.title}'

    def get_attached_models(self, field):
        if field[0] == 'facilitators':
            # Check that profile is in same site as model when adding
            profiles = field[1].objects.filter(pk__in=field[2])
            profiles = profiles.filter(pk__in=self.site.profiles().values_list('pk'))
            field.pop(2)
            return profiles
        else:
            super().get_attached_models(field)


class Theme(models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='themes')
    title = models.CharField(max_length=128)
    required_for = models.TextField(default='[]', blank=True)

    def to_dict(self):
        return model_to_dict(self)

    def __str__(self):
        return f'{self.title}'


class ProfileTheme(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='profiles')
    profile = models.ForeignKey(members_models.Profile, on_delete=models.CASCADE, related_name='themes')
    date_completed = models.DateField(blank=True, null=True)


class Module(JsonM2MFieldModelMixin, models.Model):
    JsonM2MFields = ['facilitators']
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

    def __str__(self):
        return f'{self.title}'

    def get_attached_models(self, field):
        if field[0] == 'facilitators':
            # Check that profile is in same site as model when adding
            profiles = field[1].objects.filter(pk__in=field[2])
            profiles = profiles.filter(pk__in=self.site.profiles().values_list('pk'))
            return profiles
        else:
            super().get_attached_models(field)


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
