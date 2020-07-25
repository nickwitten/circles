import json

from django.core.exceptions import ValidationError

from . import models
from django import forms
from members import models as members_models


class LearningModelForm(forms.ModelForm):
    merge_fields = ['profiles', 'facilitators_objects', 'facilitators']

    def __init__(self, *args, **kwargs):
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

    def get_fields(self):
        fields_fieldtype = {}
        fields = list(self.base_fields)
        for field in list(self.declared_fields):
            if field not in fields:
                fields.append(field)
        for field in fields:
            widget = self.fields[field].widget
            if hasattr(widget, 'input_type'):
                input_type = widget.input_type
            else:
                input_type = 'text'
            fields_fieldtype[field] = input_type
        return fields_fieldtype


class ProgrammingCreationForm(LearningModelForm):

    class Meta:
        model = models.Programming
        exclude = ('site', 'facilitators_objects')


class ThemeCreationForm(LearningModelForm):

    class Meta:
        model = models.Theme
        exclude = ('site', )


class ModuleCreationForm(LearningModelForm):

    class Meta:
        model = models.Module
        exclude = ('site', 'theme', 'facilitators_objects')
