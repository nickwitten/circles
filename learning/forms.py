from . import models
from django import forms


class SaveAttrsForm(forms.ModelForm):

    def save(self, **kwargs):
        super().save(commit=False)
        for key, value in kwargs.items():
            setattr(self.instance, key, value)
        return super().save()


class ProgrammingCreationForm(SaveAttrsForm):

    class Meta:
        model = models.Programming
        exclude = ('site', )


class ThemeCreationForm(SaveAttrsForm):

    class Meta:
        model = models.Theme
        exclude = ('site', )


class ModuleCreationForm(SaveAttrsForm):

    class Meta:
        model = models.Module
        exclude = ('site', 'theme')

