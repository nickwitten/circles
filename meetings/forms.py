from django import forms
from . import models


class MeetingCreationForm(forms.ModelForm):
    class Meta:
        model = models.Meeting
        fields = '__all__'
