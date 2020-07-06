from django.db import models
from django.forms import model_to_dict

import members.models as members_models


class AbstractProgramming(models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='programming')
    title = models.CharField(max_length=128)
    length = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)
    facilitators = models.TextField(blank=True)
    facilitator_profiles = models.ManyToManyField(members_models.Profile,
                                                  related_name='facilitate_programming', blank=True)
    link = models.TextField(blank=True)

    class Meta:
        abstract = True

    def to_dict(self):
        model_info = model_to_dict(self)
        model_info['facilitator_profiles'] = [[str(profile), profile.pk] for profile in
                                              model_info['facilitator_profiles']]
        return model_info

class Programming(AbstractProgramming):
    pass


class Theme(models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='themes')
    profiles = models.ManyToManyField(members_models.Profile, related_name='themes', blank=True)
    title = models.CharField(max_length=128)

    def to_dict(self):
        return model_to_dict(self)


class Module(AbstractProgramming):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='modules')
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='modules')
    profiles = models.ManyToManyField(members_models.Profile, related_name='modules', blank=True)
    training_for = models.CharField(choices=members_models.Role.position_choices, max_length=32, blank=True)
    facilitator_profiles = models.ManyToManyField(members_models.Profile,
                                                  blank=True, related_name='facilitate_modules')
