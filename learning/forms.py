from django.core.exceptions import ValidationError

from . import models
from django import forms


class LearningModelForm(forms.ModelForm):

    def save(self, **kwargs):
        super().save(commit=False)
        for key, value in kwargs.items():
            setattr(self.instance, key, value)
        return super().save()

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
