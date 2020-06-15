from django.db import models
from django.contrib.auth.models import User
from members.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver
from meetings.models import Meeting

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    site_access = models.ManyToManyField(Site, blank=True, related_name='site_access')

    def __str__(self):
        return f'{self.user}'

    def user_site_access(self):
        site_access = []
        sites = self.site_access.all()
        for site in sites:
            sites_chapter = site.chapter
            added = False
            for chapter in site_access:
                if chapter['chapter'] == sites_chapter:
                    chapter['sites'] += [site]
                    added = True
            if not added:
                site_access += [{'chapter': sites_chapter, 'sites': [site]}]
        return site_access

    def user_meeting_access(self):
        sites = self.site_access.all()
        meetings = Meeting.objects.filter(site__in=sites)
        return meetings

@receiver(post_save, sender=User)
def create_user_userinfo(sender, instance, created, **kwargs):
    if created:
        UserInfo.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_userinfo(sender, instance, **kwargs):
    instance.userinfo.save()