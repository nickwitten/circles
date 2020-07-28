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
                return model
            pks = [item['pk'] for item in field_value if 'pk' in item]
            attached_models = self.get_attached_models(field[1], pks)
            for pk in pks:
                if pk not in list(attached_models.values_list('pk', flat=True)):
                    pk_list = list(attached_models.values_list('pk', flat=True))
                    for j, value in enumerate(field_value):
                        if 'pk' in value and value['pk'] == pk:
                            field_value.pop(j)
            setattr(self, field[0], json.dumps(field_value))
            objects_field = getattr(self, field[0] + '_objects')
            objects_field.clear()
            objects_field.add(*attached_models)
        return super().save()

    def get_attached_models(self, klass, pks):
        return klass.objects.filter(pk__in=pks)

    def to_dict(self):
        model_info = model_to_dict(self)
        for field in self.JsonM2MFields:
            model_info.pop(field[0]+'_objects')
        return model_info


class FileFieldMixin:
    FileFields = []

    def save(self, *args, **kwargs):
        files = kwargs.pop('files', None)
        super().save(*args, **kwargs)
        if files:
            print(files)


class Programming(FileFieldMixin, JsonM2MFieldModelMixin, models.Model):
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
        self.FileFields = [ModuleFile]

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


class Theme(FileFieldMixin, models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='themes')
    title = models.CharField(max_length=128)
    required_for = models.TextField(default='[]', blank=True)

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
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

    def to_dict(self):
        return model_to_dict(self)


class ProfileTheme(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='profiles')
    profile = models.ForeignKey(members_models.Profile, on_delete=models.CASCADE, related_name='themes')
    date_completed = models.DateField(blank=True, null=True)


class Module(FileFieldMixin, JsonM2MFieldModelMixin, models.Model):
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
        self.FileFields = [ModuleFile]

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
