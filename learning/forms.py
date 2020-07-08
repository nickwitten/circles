from django.core.exceptions import ValidationError

from . import models
from django import forms


class LearningModelForm(forms.ModelForm):
    merge_fields = ['profiles', 'facilitator_profiles', 'facilitators']

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
        return super().save(commit=commit)

class ProgrammingCreationForm(LearningModelForm):

    class Meta:
        model = models.Programming
        exclude = ('site', 'profiles')


class ThemeCreationForm(LearningModelForm):

    class Meta:
        model = models.Theme
        exclude = ('site', 'profiles')


class ModuleCreationForm(LearningModelForm):

    class Meta:
        model = models.Module
        exclude = ('site', 'theme', 'profiles')
