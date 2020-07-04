from django.db import models
import members.models as members_models


class Programming(models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='programming')
    title = models.CharField(max_length=128)
    length = models.CharField(max_length=32, blank=True)
    description = models.TextField(blank=True)
    facilitators = models.TextField(blank=True)
    facilitator_profiles = models.ManyToManyField(members_models.Profile, related_name='facilitating', null=True)
    link = models.TextField(blank=True)


class Theme(models.Model):
    site = models.ForeignKey(members_models.Site, on_delete=models.CASCADE, related_name='themes')
    profiles = models.ManyToManyField(members_models.Profile, related_name='themes')
    title = models.CharField(max_length=128)


class Module(Programming):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='modules')
    profiles = models.ManyToManyField(members_models.Profile, related_name='modules')
    training_for = models.CharField(choices=members_models.Role.position_choices, max_length=32, blank=True)
