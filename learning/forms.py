import json

from django.core.exceptions import ValidationError

from . import models
from django import forms
from members import models as members_models


class JsonMany2ManyFieldForm(forms.ModelForm):
    """ Model contains a charfield where pks can be passed in that json list
        and stored in model's charfield_name + _objects"""

    JsonM2M_fields = []  # [field_name, many2many_object_cls] set in init

    def save(self, commit=True):
        """ Removes dicts from json field and adds those
            objects to manytomany relationship.  Dicts
            must contain pk key to be added to model    """
        for i, field in enumerate(self.JsonM2M_fields):
            # Grab and remove dicts from json string
            try:
                field_value = json.loads(self.cleaned_data[field[0]])
            except Exception as e:
                field_value = None
            if field_value:
                pks = []
                for j, item in enumerate(field_value):
                    if 'pk' in item:
                        object_info = field_value.pop(j)
                        pks.append(object_info['pk'])
                setattr(self.instance, field[0], json.dumps(field_value))
                self.JsonM2M_fields[i].append(pks)
            else:
                self.JsonM2M_fields[i].append([])
        # Save and add objects with those pks to model
        model = super().save(commit)
        if commit:
            for field in self.JsonM2M_fields:
                attached_models = self.get_attached_models(field)
                objects_field = getattr(self.instance, field[0] + '_objects')
                objects_field.clear()
                objects_field.add(*attached_models)
        return model

    def get_attached_models(self, field):
        return field[1].objects.filter(pk__in=field[2])


class LearningModelForm(JsonMany2ManyFieldForm):
    merge_fields = ['profiles', 'facilitators_objects', 'facilitators']

    def __init__(self, *args, **kwargs):
        self.JsonM2M_fields = [['facilitators', members_models.Profile]]
        super().__init__(*args, **kwargs)
        required_fields = []
        for field_name, field in self.fields.items():
            if field.required:
                required_fields.append(field_name)
        self.required_fields = required_fields

    def save(self, commit=True, **kwargs):
        super().save(commit=False)
        for key, value in kwargs.items():
            setattr(self.instance, key, value)
        return super().save(commit)

    def get_attached_models(self, field):
        if field[0] == 'facilitators':
            # Check that profile is in same site as model when adding
            profiles = field[1].objects.filter(pk__in=field[2])
            profiles = profiles.filter(pk__in=self.instance.site.profiles().values_list('pk'))
            return profiles
        else:
            super().get_attached_models(field)


class ProgrammingCreationForm(LearningModelForm):

    class Meta:
        model = models.Programming
        exclude = ('site', 'profiles', 'facilitators_objects')


class ThemeCreationForm(LearningModelForm):

    class Meta:
        model = models.Theme
        exclude = ('site', 'profiles')


class ModuleCreationForm(LearningModelForm):

    class Meta:
        model = models.Module
        exclude = ('site', 'theme', 'profiles', 'facilitators_objects')
