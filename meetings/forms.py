from django import forms
from . import models


class MeetingCreationForm(forms.ModelForm):
    type_choices = ['Big View', 'Test', 'Custom Type']

    class Meta:
        model = models.Meeting
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].widget.attrs['oninput'] = 'expandTitle();'
        self.fields['type'].widget.attrs['class'] = 'expanding_input'
        self.fields['type'].widget.attrs['placeholder'] = 'Type'
        self.fields['start_time'].widget.attrs['class'] = 'start_time'
        self.fields['end_time'].widget.attrs['class'] = 'end_time'
        self.fields['site'].widget.attrs['class'] = 'form-control'
        self.fields['location'].widget.attrs['class'] = 'form-control'
        self.fields['notes'].widget.attrs['class'] = 'form-control'
