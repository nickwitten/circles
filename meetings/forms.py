from django import forms
from django.db.models.query import QuerySet

from dashboard.forms import CustomFormMixin
from . import models


class MeetingCreationForm(CustomFormMixin, forms.ModelForm):
    type_choices = ['Big View', 'Test', 'Custom Type']

    class Meta:
        model = models.Meeting
        exclude = ('programming_objects', 'modules_objects', 'attendees_objects',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        data = False
        if 'data' in kwargs:
            data = True
        super().__init__(*args, **kwargs)
        dynamic_model_fields = ['attendees', 'programming', 'modules']
        if not data:
            for field in dynamic_model_fields:
                # Don't render all objects
                self.fields[field].queryset = self.fields[field].queryset.model.objects.none()
        self.fields['site'].queryset = user.userinfo.user_site_access()
        self.fields['lists'].queryset = user.filtersets.all()
        self.fields['type'].widget.attrs['oninput'] = 'expandTitle("Type");'
        self.fields['type'].widget.attrs['class'] = 'expanding_input'
        self.fields['type'].widget.attrs['placeholder'] = 'Type'
        self.fields['type'].widget.attrs['readonly'] = 'readonly'
        self.fields['start_time'].widget.attrs['class'] = 'start_time'
        self.fields['end_time'].widget.attrs['class'] = 'end_time'
