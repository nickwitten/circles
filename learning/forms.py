import json

from django.core.exceptions import ValidationError

from dashboard.forms import CustomFormMixin
from . import models
from django import forms
from members import models as members_models


class LearningModelForm(CustomFormMixin, forms.ModelForm):
    merge_fields = ['profiles', 'facilitators_objects', 'facilitators']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = []
        for field_name, field in self.fields.items():
            if field.required:
                required_fields.append(field_name)
        self.required_fields = required_fields

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
