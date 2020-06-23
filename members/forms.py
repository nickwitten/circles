from django import forms
from bootstrap_modal_forms.forms import BSModalForm
from .models import Profile, Residence, Role, Training, Child, ChildInfo, Site
from .data import form_choices_text


class RoleCreationForm(BSModalForm):

    class Meta:
        model = Role
        exclude = ('profile',)
        labels = {
        "end_date":"End date (leave empty if current)"
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RoleCreationForm, self).__init__(*args, **kwargs)
        if user:
            sites = user.userinfo.user_site_access()
            self.fields['site'] = forms.ModelChoiceField(sites)
        for visible in self.visible_fields():
            #gives text input crispy classes
            visible.field.widget.attrs['class'] = "form-field textinput textInput form-control"


class ProfileCreationForm(forms.ModelForm):
    site = forms.ModelChoiceField(Site.objects.all())
    position = forms.ChoiceField(choices=[('','---------')] + Role.position_choices)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            sites = user.userinfo.user_site_access()
            self.fields['site'] = forms.ModelChoiceField(sites)
        for visible in self.visible_fields():
            #gives text input crispy classes
            visible.field.widget.attrs['class'] = "form-field textinput textInput form-control"

    class Meta:
        model = Profile
        fields = '__all__'
        labels = {
            "circles_id":"Circles ID",
            "birthdate":"DOB",
            "other_phone":"Other phone",
            "email":"Email address",
            "cell":"Cell phone",
            "e_relationship":"Relationship",
            "e_first_name":"First name",
            "e_last_name":"Last name",
            "e_phone":"Phone number",
        }

class ProfileUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():

            #gives text input crispy classes
            visible.field.widget.attrs['class'] = "form-field textinput textInput form-control"

    class Meta:
        model = Profile
        fields = '__all__'
        labels = {
            "circles_id":"Circles ID",
            "birthdate":"DOB",
            "other_phone":"Other phone",
            "email":"Email address",
            "cell":"Cell phone",
            "e_relationship":"Relationship",
            "e_first_name":"First name",
            "e_last_name":"Last name",
            "e_phone":"Phone number",
        }


class ResidenceCreationForm(BSModalForm):

    class Meta:
        model = Residence
        #fields = '__all__'
        exclude = ('profile',)
        labels = {
        "end_date":"End date (leave empty if current)"
        }

    def __init__(self, *args, **kwargs):
        super(ResidenceCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():

            #gives text input crispy classes
            visible.field.widget.attrs['class'] = "form-field textinput textInput form-control"


class TrainingAddForm(BSModalForm):

    class Meta:
        model = Training
        exclude = ('profile',)
        labels = {
        }

    def __init__(self, *args, **kwargs):
        super(TrainingAddForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():

            #gives text input crispy classes
            visible.field.widget.attrs['class'] = "form-field textinput textInput form-control"

class ChildCreationForm(forms.ModelForm):

    class Meta:
        model = Child
        exclude = ('child_info',)
        labels = {
        }

    def __init__(self, *args, **kwargs):
        super(ChildCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():

            #gives text input crispy classes
            visible.field.widget.attrs['class'] = "form-field textinput textInput form-control"

class ChildInfoCreationForm(BSModalForm):

    class Meta:
        model = ChildInfo
        #fields = '__all__'
        exclude = ('profile',)
        labels = {
        }

    def __init__(self, *args, **kwargs):
        super(ChildInfoCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():

            #gives text input crispy classes
            visible.field.widget.attrs['class'] = "form-field textinput textInput form-control"

class ProfilesToolsForm(forms.Form):
    searchinput = forms.CharField(required=False,
                                  widget=forms.TextInput(attrs={
                                    'class':"form-control",
                                    'aria-describedby':'basic-addon1',
                                  }))
    filters = forms.CharField(required=False)
    datatype = forms.CharField(required=False)
    sortby = forms.ChoiceField(required=False,
                               choices=form_choices_text,
                               widget=forms.Select(attrs={
                                'class':'form-control',
                                'type':'text',
                                'placeholder':'Sort By',
                                'default':None,
                               }))
