from django import forms
from bootstrap_modal_forms.forms import BSModalModelForm
from .models import Profile, Residence, Role, Child, ChildInfo, Site, FilterSet, Chapter
from django.contrib.auth.models import User
from .data import form_choices_text


class FieldStyleMixin:

    def field_styles(self):
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = "form-control"

class ChapterCreationForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = '__all__'

class SiteCreationForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = '__all__'

class RoleCreationForm(FieldStyleMixin, BSModalModelForm):
    class Meta:
        model = Role
        exclude = ('profile',)
        labels = {
            "end_date": "End date (leave empty if current)"
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            sites = user.userinfo.user_site_access()
            profiles = user.userinfo.user_profile_access()
            self.fields['site'] = forms.ModelChoiceField(sites)
        self.field_styles()


class ProfileCreationForm(FieldStyleMixin, forms.ModelForm):
    site = forms.ModelChoiceField(None)
    position = forms.ChoiceField(choices=[('', '---------')] + Role.position_choices)

    class Meta:
        model = Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            sites = user.userinfo.user_site_access()
            self.fields['site'] = forms.ModelChoiceField(sites)
        self.field_styles()

class ProfileUpdateForm(FieldStyleMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_styles()

class ResidenceCreationForm(FieldStyleMixin, BSModalModelForm):
    class Meta:
        model = Residence
        # fields = '__all__'
        exclude = ('profile',)
        labels = {
            "end_date": "End date (leave empty if current)"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_styles()


class ChildCreationForm(FieldStyleMixin, forms.ModelForm):
    class Meta:
        model = Child
        exclude = ('child_info',)
        labels = {
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_styles()

class ChildInfoCreationForm(FieldStyleMixin, BSModalModelForm):
    class Meta:
        model = ChildInfo
        # fields = '__all__'
        exclude = ('profile',)
        labels = {
        }

    def __init__(self, *args, **kwargs):
        super(ChildInfoCreationForm, self).__init__(*args, **kwargs)
        self.field_styles()

class ProfilesToolsForm(forms.Form):
    searchinput = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={
                                      'class': "form-control",
                                      'aria-describedby': 'basic-addon1',
                                  }))
    filters = forms.CharField(required=False)
    datatype = forms.CharField(required=False)
    sortby = forms.ChoiceField(required=False,
                               choices=form_choices_text,
                               widget=forms.Select(attrs={
                                   'class': 'form-control',
                                   'type': 'text',
                                   'placeholder': 'Sort By',
                                   'default': None,
                               }))


class UserListForm(forms.ModelForm):
    class Meta:
        model = FilterSet
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].required = False

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().save(commit=False)
        if user:
            self.instance.user = user
        return super().save(*args, **kwargs)
