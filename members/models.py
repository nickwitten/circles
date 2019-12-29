from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image
from datetime import date

# Create your models here.

class Profile(models.Model):
    first_name = models.CharField(max_length = 20)
    last_name = models.CharField(max_length = 20)
    circles_id = models.CharField(blank=True,null=True,max_length = 6)
    birthdate = models.DateField(blank=True,null=True)
    race = models.CharField(blank=True,null=True,max_length=10,choices=[('white','White',),('black','Black'),('other','Other')])
    gender = models.CharField(blank=True,null=True,max_length=8,choices=[('male','Male'),('female','Female'),('other','Other')])
    email = models.EmailField(blank=True,null=True)
    cell = PhoneNumberField(blank=True,null=True)
    other_phone = PhoneNumberField(blank=True,null=True)
    site = models.CharField(blank=True,null=True,max_length = 20)
    image = models.ImageField(default='default.jpg',upload_to='profile_pics')
    e_relationship = models.CharField(blank=True,null=True,max_length=10,choices=[('friend','Friend',),('parent','Parent'),('sibling','Sibling')])
    e_first_name = models.CharField(blank=True,null=True,max_length = 20)
    e_last_name = models.CharField(blank=True,null=True,max_length = 20)
    e_phone = PhoneNumberField(blank=True,null=True)
    status = models.CharField(blank=True,null=True,max_length=16,choices=[('potential','Potential'),('active','Active'),('inactive','Inactive')])

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_absolute_url(self):
        return reverse('profile-detail',kwargs={'pk':self.pk})

    def save(self):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def order_residences(self):
        return self.residences.order_by('-start_date')


    def order_roles(self):
        return self.roles.order_by('-start_date')

    def order_training(self):
        return self.training.order_by('-date_completed')

    # Get all ChildInfos
    def get_child_infos(self):
        return self.childinfos.all()

    # Get all Children
    def order_children(self):
        children = []
        # Loop through all childinfos
        for childinfo in self.childinfos.all():
            # Loop through all children in childinfos
            for child in childinfo.order_children():
                children.append(child) # Add child to the list
        return children

class Residence(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='residences')
    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    street_address = models.CharField(max_length=64)
    unit = models.CharField(blank=True,max_length=16)
    city = models.CharField(max_length=32)
    state = models.CharField(max_length=32)
    zip = models.CharField(max_length=5)
    ownership = models.CharField(blank=True,null=True,max_length=16,choices=[('N/A','N/A'),('Rent','Rent'),('Own','Own'),('Doubled','Doubled')],default='N/A')
    habitat = models.CharField(max_length=8,choices=[('N/A','N/A'),('Yes','Yes'),('No','No'),],default='N/A')
    safe = models.CharField(max_length=8,choices=[('N/A','N/A'),('Yes','Yes'),('No','No'),],default='N/A')
    repair = models.CharField(max_length=8,choices=[('N/A','N/A'),('Yes','Yes'),('No','No'),],default='N/A')
    payment = models.CharField(blank=True,null=True,max_length=16)

    def __str__(self):
        return f'{self.street_address}'

class Role(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='roles')
    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    position = models.CharField(max_length=64,choices=[('circle leader','Circle leader'),('ally','Ally'),('volunteer','Volunteer'),('resource team','Resource team'),('donor','Donor')])
    cohort = models.CharField(blank=True,null=True,max_length = 6, choices = [('cl','CL'),('ally', 'Ally')])
    resource_team_name = models.CharField(blank=True,null=True,max_length = 16)
    resource_team_role = models.CharField(blank=True,null=True,max_length = 16)
    location = models.CharField(blank=True,null=True,max_length = 16)


    def __str__(self):
        return f'{self.profile} {self.start_date}'

class Training(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='training')
    subject = models.CharField(blank=True,null=True,max_length = 32)
    date_completed = models.DateField(blank=True,null=True)

    def __str__(self):
        return f'{self.profile} {self.start_date}'

class ChildInfo(models.Model):
    profile = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='childinfos')
    parent_first_name = models.CharField(blank=True,null=True,max_length = 16)
    parent_last_name = models.CharField(blank=True,null=True,max_length = 16)
    parent_phone = PhoneNumberField(blank=True,null=True)
    parent_street_address = models.CharField(blank=True,null=True,max_length=64)
    parent_unit = models.CharField(blank=True,null=True,max_length=16)
    parent_city = models.CharField(blank=True,null=True,max_length=32)
    parent_state = models.CharField(blank=True,null=True,max_length=32)
    parent_zip = models.CharField(blank=True,null=True,max_length=5)
    e_relationship = models.CharField(blank=True,null=True,max_length=10,choices=[('friend','Friend',),('parent','Parent'),('sibling','Sibling')])
    e_first_name = models.CharField(blank=True,null=True,max_length = 20)
    e_last_name = models.CharField(blank=True,null=True,max_length = 20)
    e_phone = PhoneNumberField(blank=True,null=True)
    physician_name = models.CharField(blank=True,null=True,max_length=32)
    physician_practice = models.CharField(blank=True,null=True,max_length=64)
    physician_phone = PhoneNumberField(blank=True,null=True)

    def order_children(self):
        return self.children.order_by('-birthdate')


class Child(models.Model):
    child_info = models.ForeignKey(ChildInfo,on_delete=models.CASCADE,related_name='children')
    first_name = models.CharField(max_length = 16)
    last_name = models.CharField(max_length = 16)
    middle_name = models.CharField(max_length = 16)
    relationship = models.CharField(blank=True,null=True,max_length=10,choices=[('child','Child'),('grandchild','Grandchild'),('other related','Other Related'),('other','Other')])
    attendance = models.CharField(blank=True,null=True,max_length=10,choices=[('active','Active'),('inactive','Inactive')])
    birthdate = models.DateField(blank=True,null=True)
    gender = models.CharField(blank=True,null=True,max_length=8,choices=[('male','Male'),('female','Female'),('other','Other')])
    health_issues = models.TextField(blank=True,null=True)
    physical_date = models.DateField(blank=True,null=True)
    allergies = models.TextField(blank=True,null=True)
    medications = models.TextField(blank=True,null=True)
    dietary_modifications = models.TextField(blank=True,null=True)
    disabilities = models.TextField(blank=True,null=True)

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

class FilterSet(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='filtersets')
    title = models.CharField(max_length=32)
    filterset = models.CharField(max_length=512)

    def __str__(self):
        return f'{self.user.username} {self.title}'
