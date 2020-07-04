from . import models
from django import forms


class ProgrammingCreationForm(forms.ModelForm):

    class Meta:
        model = models.Module
        fields = '__all__'


class ThemeCreationForm(forms.ModelForm):

    class Meta:
        model = models.Module
        fields = '__all__'


class ModuleCreationForm(forms.ModelForm):

    class Meta:
        model = models.Module
        fields = '__all__'
