from django import forms
from . import models


class MeetingCreationForm(forms.ModelForm):
    class Meta:
        model = models.Meeting
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = ''
        self.fields['title'].widget.attrs['oninput'] = 'expandTitle();'
        self.fields['title'].widget.attrs['class'] = 'expanding_input'
        self.fields['title'].widget.attrs['placeholder'] = 'Title'
        self.fields['start_time'].widget.attrs['class'] = 'start_time'
        self.fields['end_time'].widget.attrs['class'] = 'end_time'
