import json
import os
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files import File
from io import BytesIO
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image
from datetime import date
from circles import settings

class Chapter(models.Model):
    chapter = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.chapter}'

class Site(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='sites', null=True)
    site = models.CharField(max_length=64)

    def profiles(self):
        return Profile.objects.filter(roles__site=self).distinct()

    def __str__(self):
        return f'{self.site}'

class Profile(models.Model):  # ForeignKey field must have same name as related model
    circles_ID = models.CharField(blank=True,null=True,max_length = 16)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    DOB = models.DateField(blank=True,null=True)
    gender = models.CharField(blank=True,null=True,max_length=16,choices=[('Male','Male'),('Female','Female'),('Non-Binary','Non-Binary')])
    race = models.CharField(blank=True,null=True,max_length=128,choices=[
        ('Asian American/Pacific Islander/Asian','Asian American/Pacific Islander/Asian'),
        ('Black/African American/African','Black/African American/African'),
        ('Hispanic/Latinx/Chicanx','Hispanic/Latinx/Chicanx'),
        ('Middle Eastern/Middle Eastern American', 'Middle Eastern/Middle Eastern American'),
        ('Native American/American Indian/Indigenous', 'Native American/American Indian/Indigenous'),
        ('Other', 'Other'),
        ('White/Caucasian/European', 'White/Caucasian/European')
    ])
    email_address = models.EmailField(blank=True,null=True)
    cell_phone = PhoneNumberField(blank=True,null=True)
    other_phone = PhoneNumberField(blank=True,null=True)
    image = models.ImageField(blank=True, null=True, default=os.path.join(settings.MEDIA_ROOT, 'profile_pics/default.jpg'), upload_to='profile_pics')
    e_relationship = models.CharField(blank=True,null=True,max_length=10,choices=[('Spouse', 'Spouse'), ('Friend','Friend'),('Parent','Parent'),('Sibling','Sibling')])
    e_first_name = models.CharField(blank=True,null=True,max_length=32)
    e_last_name = models.CharField(blank=True,null=True,max_length=32)
    e_phone = PhoneNumberField(blank=True,null=True)
    status = models.CharField(blank=True,null=True,max_length=16,choices=[('Potential','Potential'),('Active','Active'),('Inactive','Inactive')])
    main_fields = ['first_name', 'last_name', 'DOB', 'gender', 'race', 'email_address',
                   'cell_phone', 'other_phone',]
    e_fields = ['e_relationship', 'e_first_name', 'e_last_name', 'e_phone',]
    third_fields = ['DOB', 'gender', 'race',]
    half_fields = ['circles_ID', ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_absolute_url(self):
        return reverse('profile-detail',kwargs={'pk':self.pk})

    def save(self, *args, **kwargs):
        self.image = self.crop_image(self.image)
        super().save(*args, **kwargs)

    def crop_image(self, image):
        img = Image.open(image)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.convert('RGBA')
            img_io = BytesIO()
            img.save(img_io, 'PNG', quality=95)
            return File(img_io, name=image.name)
        else:
            return self.image

    def add_learning(self, learning, profile_learning_class, end_date):
        if learning.site not in self.sites():
            print(str(self) + ' does not belong to site: ' + str(learning.site))
            return False
        profile_learning = learning.profiles.filter(profile=self).first()
        if profile_learning and profile_learning.end_date:
            return False
        else:
            pk = profile_learning.pk if profile_learning else None
            attrs = {learning.__class__.__name__.lower(): learning, 'profile': self, 'end_date': end_date}
            obj, created = profile_learning_class.objects.update_or_create(pk=pk, defaults=attrs)
            obj.save()
            return True

    def remove_learning(self, learning):
        profile_learning = learning.profiles.filter(profile=self).first()
        if not profile_learning:
            return
        required_for = json.loads(learning.required_for)
        if self.roles.filter(position__in=required_for):
            # Don't delete just remove date completed
            profile_learning.end_date = None
            profile_learning.save(theme_remove=True)
        else:
            profile_learning.delete()

    def sites(self):
        sites = [role.site.pk for role in self.roles.all()]
        return Site.objects.filter(pk__in=sites).order_by('site')

    def order_residences(self):
        return self.residences.order_by('-start_date')

    def order_roles(self):
        return self.roles.order_by('-start_date')

    def order_training(self):
        trainings = []
        for site in self.sites():
            temp_site = {'site': site, 'themes': []}
            for theme in site.themes.order_by('title'):
                temp_theme = {'theme': theme, 'profile_theme': theme.profiles.filter(profile=self).first(), 'profile_modules': theme.order_open_modules(self)}
                if temp_theme['profile_modules']:
                    temp_site['themes'] += [temp_theme]
            if temp_site['themes']:
                trainings += [temp_site]
            print(trainings)
        return trainings

    def get_child_infos(self):
        return self.childinfos.all()

    def order_children(self):
        return Child.objects.filter(child_info__profile=self)


class Residence(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='residences')
    street_address = models.CharField(max_length=64)
    unit = models.CharField(blank=True,max_length=16)
    city = models.CharField(max_length=32)
    state = models.CharField(max_length=32)
    zip = models.CharField(max_length=16)
    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    ownership = models.CharField(blank=True,null=True,max_length=16,choices=[('N/A','N/A'),('Rent','Rent'),('Own','Own'),('Doubled','Doubled')],default='N/A')
    monthly_payment = models.CharField(blank=True,null=True,max_length=16)
    habitat = models.CharField(blank=True,null=True, max_length=8,choices=[('N/A','N/A'),('Yes','Yes'),('No','No'),],default='N/A')
    safety = models.CharField(blank=True,null=True, max_length=8,choices=[('N/A','N/A'),('Yes','Yes'),('No','No'),],default='N/A')
    repair = models.CharField(blank=True,null=True, max_length=8,choices=[('N/A','N/A'),('Yes','Yes'),('No','No'),],default='N/A')
    display_fields = ['ownership', 'habitat', 'safety', 'repair', 'monthly_payment',]

    def __str__(self):
        return f'{self.street_address}'

    @staticmethod
    def get_related(profile):
        return profile.order_residences()

    def dates(self):
        dates = ''
        if self.start_date:
            dates = self.start_date.format('m/d/Y')
            if self.end_date:
                dates += ' - ' + self.end_date.format('m/d/Y')


class Role(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='roles')
    site = models.ForeignKey(Site,on_delete=models.SET_NULL, null=True, related_name='roles')
    position_choices = [('Ally','Ally'), ('Circle Leader','Circle Leader'), ('Donor','Donor'), ('Facilitator', 'Facilitator'), ('Resource Team','Resource Team'), ('Staff', 'Staff'), ('Volunteer','Volunteer'), ('Other','Other')]
    position = models.CharField(max_length=64,choices=position_choices)
    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    # cohort = models.CharField(blank=True,null=True,max_length=32, choices=[('CL','CL'),('Ally', 'Ally')])
    cohort = models.IntegerField(blank=True,null=True)
    resource_team_name = models.CharField(blank=True,null=True,max_length=32)
    resource_team_role = models.CharField(blank=True,null=True,max_length=32)
    display_fields = ['cohort', 'resource_team_name', 'resource_team_role', 'site',]

    def __str__(self):
        return f'{self.profile} {self.start_date}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_required_training()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_required_training()

    def update_required_training(self):
        modules = self.site.modules.all()
        themes = self.site.themes.all()
        for learn_type in [modules, themes]:
            for item in learn_type:
                profile_connection = item.profiles.filter(profile=self.profile).first()
                required_positions = json.loads(item.required_for)
                if self.profile.roles.filter(position__in=required_positions):
                    if not profile_connection:
                        item.create_profile_connection(self.profile)
                elif profile_connection and not profile_connection.end_date:
                    profile_connection.delete()


    @staticmethod
    def get_related(profile):
        return profile.order_roles()


class ChildInfo(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='childinfos')
    parent_first_name = models.CharField(blank=True,null=True,max_length=16)
    parent_last_name = models.CharField(blank=True,null=True,max_length=16)
    parent_phone = PhoneNumberField(blank=True,null=True)
    parent_street_address = models.CharField(blank=True,null=True,max_length=64)
    parent_unit = models.CharField(blank=True,null=True,max_length=16)
    parent_city = models.CharField(blank=True,null=True,max_length=32)
    parent_state = models.CharField(blank=True,null=True,max_length=32)
    parent_zip = models.CharField(blank=True,null=True,max_length=8)
    e_relationship = models.CharField(blank=True,null=True,max_length=16,choices=[('Friend','Friend',),('Parent','Parent'),('Sibling','Sibling')])
    e_first_name = models.CharField(blank=True,null=True,max_length=32)
    e_last_name = models.CharField(blank=True,null=True,max_length=32)
    e_phone = PhoneNumberField(blank=True,null=True)
    physician_name = models.CharField(blank=True,null=True,max_length=32)
    physician_practice = models.CharField(blank=True,null=True,max_length=64)
    physician_phone = PhoneNumberField(blank=True,null=True)

    def order_children(self):
        return self.children.order_by('-birthdate')

class Child(models.Model):
    child_info = models.ForeignKey(ChildInfo,on_delete=models.CASCADE,related_name='children')
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    middle_name = models.CharField(max_length=32)
    relationship = models.CharField(blank=True,null=True,max_length=16,choices=[('Child','Child'),('Grandchild','Grandchild'),('Other Related','Other Related'),('Other','Other')])
    attendance = models.CharField(blank=True,null=True,max_length=16,choices=[('active','Active'),('inactive','Inactive')])
    birthdate = models.DateField(blank=True,null=True)
    gender = models.CharField(blank=True,null=True,max_length=8,choices=[('Male','Male'),('Female','Female'),('Other','Other')])
    known_health_issues = models.TextField(blank=True,null=True)
    date_of_last_physical_exam = models.DateField(blank=True,null=True)
    allergies = models.TextField(blank=True,null=True)
    medications = models.TextField(blank=True,null=True)
    dietary_modifications = models.TextField(blank=True,null=True)
    disabilities = models.TextField(blank=True,null=True)
    nonvisible_fields = ['id', 'child_info', 'first_name', 'last_name', 'middle_name', 'disabilities']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def calculate_age(self):
        today = date.today()
        if self.birthdate == None:
            return 'Not Available'
        else:
            return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))

    def middle_initial(self):
        return self.middle_name[0]

    @staticmethod
    def get_related(profile):
        return profile.order_children()

    def get_display_fields(self):
        fields = []
        for field in self._meta.get_fields():
            if field.name not in self.nonvisible_fields:
                value = getattr(self, field.name)
                value = value if value else ''
                try:
                    value = value.capitalize()
                except:
                    pass
                label = ' '.join(field.name.split('_')).capitalize()
                label = label + ':'
                fields += [(label, value)]
        return fields


class FilterSet(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='filtersets')
    title = models.CharField(max_length=32, null=True, blank=True)
    filters = models.TextField(default='[]')

    def __str__(self):
        return f'{self.title}'
