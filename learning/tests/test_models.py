from learning import models
from members.tests.test_models import CreateChaptersMixin, CreateProfilesMixin


class CreateLearningModelsMixin(CreateProfilesMixin, CreateChaptersMixin):
    model_ct = 2

    """ Creates programming and training for each site

        programming1
        programming2
        theme1
            module1
            module2
        theme2
            module1
            module2

    """

    def create_learning_models(self):
        self.create_chapters()
        self.create_profiles()
        i = -1
        for site in self.sites.values():
            access = site in self.user.userinfo.user_site_access()
            if access:
                i += 1
            for j in range(self.model_ct):
                facilitator = site.roles.first().profile
                programming = models.Programming.objects.create(
                    site=site,
                    title="programming" + str(j+1),
                )
                programming.facilitator_profiles.add(facilitator)
                if access:
                    setattr(self, 'programming' + str(i+1) + '_' + str(j+1), programming)
                theme = models.Theme.objects.create(
                    site=site,
                    title="theme" + str(j+1),
                )
                if access:
                    setattr(self, 'theme' + str(i+1) + '_' + str(j+1), theme)
                for k in range(self.model_ct):
                    module = models.Module.objects.create(
                        site=site,
                        title="module" + str(k+1),
                        theme=theme,
                    )
                    module.facilitator_profiles.add(facilitator)
                    if access:
                        setattr(
                            self,
                            'module' + str(i+1) + '_' + str(j+1) + '_' + str(k+1),
                            module)
