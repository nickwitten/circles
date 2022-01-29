from django.db import models
from django.contrib.auth.models import User
from members.models import Site, Chapter
from django.db.models.signals import post_save
from django.dispatch import receiver
from meetings.models import Meeting
from members.models import Profile

class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    site_access = models.ManyToManyField(Site, blank=True, related_name='site_access')

    def __str__(self):
        return f'{self.user}'

    def user_site_access(self):
        if self.user.is_superuser:
            return Site.objects.all()
        return self.site_access.all()

    def user_site_access_dict(self):
        site_access = []
        sites = self.user_site_access()
        for site in sites:
            sites_chapter = site.chapter
            site_dict = {'pk': site.pk, 'str': str(site)}
            added = False
            for chapter in site_access:
                if chapter['pk'] == sites_chapter.pk:
                    chapter['sites'] += [site_dict]
                    added = True
            if not added:
                site_access += [{'pk':sites_chapter.pk, 'str': str(sites_chapter), 'sites': [site_dict]}]
        if self.user.is_superuser:
            # If the user is a superuser add empty chapters as well.  Helpful when creating new chapters.
            site_access += [{'pk': chapter.pk, 'str': str(chapter), 'sites': []} for chapter in Chapter.objects.filter(sites=None)]
        return site_access

    def user_meeting_access(self):
        sites = self.user_site_access()
        meetings = Meeting.objects.filter(site__in=sites)
        return meetings

    def user_profile_access(self):
        sites = self.user_site_access()
        # Need to check if it has a role with site field in sites
        profiles = Profile.objects.filter(roles__site__in=sites).distinct()
        return profiles

@receiver(post_save, sender=User)
def create_user_userinfo(sender, instance, created, **kwargs):
    if created:
        UserInfo.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_userinfo(sender, instance, **kwargs):
    instance.userinfo.save()
