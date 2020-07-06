from members import models


class CreateChaptersMixin:
    visible_chapter_ct = 1
    visible_site_ct = 2
    chapters = {}
    sites = {}

    """ Creates two chapters:
    
        chapter_access1 
            site_access1
            site_access2
            site_noaccess_in_chapter_access1
            site_noaccess_in_chapter_access2
            
        chapter_noaccess1
            site_noaccess1 """

    def create_chapters(self):
        for i in range(self.visible_chapter_ct):
            self.chapters['chapter_access' + str(i+1)] = models.Chapter.objects.create(
                chapter='chapter_access' + str(i+1)
            )
            self.chapters['chapter_noaccess' + str(i+1)] = models.Chapter.objects.create(
                chapter='chapter_noaccess' + str(i+1)
            )
            self.sites['site_noaccess' + str(i+1)] = models.Site.objects.create(
                site="site_noaccess" + str(i+1),
                chapter=self.chapters['chapter_noaccess' + str(i+1)]
            )
            for j in range(self.visible_site_ct):
                self.sites['site_access' + str(j+1)] = models.Site.objects.create(
                    site="site_access" + str(j+1),
                    chapter=self.chapters['chapter_access' + str(i+1)]
                )
                self.user.userinfo.site_access.add(self.sites['site_access' + str(j+1)])
                self.sites['site_noaccess_in_chapter_access' + str(j+1)] = models.Site.objects.create(
                    site="site_noaccess_in_chapter_access" + str(j+1),
                    chapter=self.chapters['chapter_access' + str(i+1)]
                )


class CreateProfilesMixin:
    profile_ct = 2
    profiles = {}

    """ Creates profiles with corresponding roles for every site"""

    def create_profiles(self):
        for site in self.sites.values():
            for i in range(self.profile_ct):
                profile = models.Profile.objects.create(
                    first_name='profile',
                    last_name=str(i+1),
                )
                models.Role.objects.create(
                    profile=profile,
                    site=site,
                    position=models.Role.position_choices[0],
                )
