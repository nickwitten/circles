from django import forms

from dashboard.forms import CustomFormMixin
from . import models


class MeetingCreationForm(CustomFormMixin, forms.ModelForm):
    type_choices = ['Big View', 'Test', 'Custom Type']

    class Meta:
        model = models.Meeting
        exclude = ('programming_objects', 'module_objects')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['site'] = forms.ModelChoiceField(user.userinfo.user_site_access())
        self.fields['type'].widget.attrs['oninput'] = 'expandTitle("Type");'
        self.fields['type'].widget.attrs['class'] = 'expanding_input'
        self.fields['type'].widget.attrs['placeholder'] = 'Type'
        self.fields['type'].widget.attrs['readonly'] = 'readonly'
        self.fields['start_time'].widget.attrs['class'] = 'start_time'
        self.fields['end_time'].widget.attrs['class'] = 'end_time'
