import json
import os
from audioop import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client

from circles import settings
from learning import models
from members.tests.test_models import CreateChaptersMixin, CreateProfilesMixin


class CreateLearningModelsMixin(CreateProfilesMixin, CreateChaptersMixin):
    model_ct = 2

    """ Creates programming and training for each site

        programming1    (self.programming1_1))
        programming2
        theme1          (self.theme1_1)
            module1     (self.module1_1_1)
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
                    title="programming" + str(j + 1),
                    facilitators='[{"pk": ' + str(facilitator.pk) + ', "name": "' + str(facilitator) + '"}]',
                )
                programming.facilitators_objects.add(facilitator)
                if access:
                    setattr(self, 'programming' + str(i + 1) + '_' + str(j + 1), programming)
                theme = models.Theme.objects.create(
                    site=site,
                    title="theme" + str(j + 1),
                )
                if access:
                    setattr(self, 'theme' + str(i + 1) + '_' + str(j + 1), theme)
                for k in range(self.model_ct):
                    module = models.Module.objects.create(
                        site=site,
                        title="module" + str(k + 1),
                        theme=theme,
                        facilitators='[{"pk": ' + str(facilitator.pk) + ', "name": "' + str(facilitator) + '"}]',
                    )
                    module.facilitators_objects.add(facilitator)
                    if access:
                        setattr(
                            self,
                            'module' + str(i + 1) + '_' + str(j + 1) + '_' + str(k + 1),
                            module)


class TestModels(CreateLearningModelsMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='password')
        self.create_learning_models()

    def test_programming_to_dict(self):
        info = self.programming1_1.to_dict()
        self.assertEqual(info, {
            'id': 3,
            'site': 2,
            'title': 'programming1',
            'length': '',
            'description': '',
            'facilitators': '[{"pk": 3, "name": "profile 1"}]',
            'links': '[]',
        })

    def test_theme_to_dict(self):
        info = self.theme1_1.to_dict()
        self.assertEqual(info, {
            'id': 3,
            'site': 2,
            'title': 'theme1',
            'required_for': '[]'
        })

    def test_module_to_dict(self):
        info = self.module1_1_1.to_dict()
        self.assertEqual(info, {
            'id': 5,
            'site': 2,
            'theme': 3,
            'required_for': '[]',
            'title': 'module1',
            'length': '',
            'description': '',
            'facilitators': '[{"pk": 3, "name": "profile 1"}]',
            'links': '[]',
        })

    def test_programming_facilitators_save(self):
        programming = self.programming1_1
        programming.facilitators_objects.clear()
        self.assertEqual(programming.facilitators_objects.count(), 0)
        programming.facilitators = '[{"pk":3, "name": "profile 1"}]'
        programming.save()
        self.assertEqual(programming.facilitators_objects.count(), 1)

    def test_theme_required_for_save(self):
        theme = self.theme1_1
        module = self.module1_1_1
        module.required_for = '["Circle Leader"]'
        module.save()
        theme.required_for = '["Ally"]'
        theme.save()
        module.refresh_from_db()
        self.assertCountEqual(json.loads(module.required_for), json.loads('["Circle Leader", "Ally"]'))

    def test_module_required_for_save(self):
        self.test_theme_required_for_save()
        self.module1_1_1.required_for = '[]'
        self.module1_1_1.save()
        self.theme1_1.refresh_from_db()
        self.assertEqual(self.theme1_1.required_for, '[]')

    def test_programming_file_delete(self):
        with open(settings.MEDIA_ROOT + "/learning_files/test12345.txt", "w+") as f:
            f.write('Test')
            f.close()
        self.assertEqual(os.path.exists(settings.MEDIA_ROOT + "/learning_files/test12345.txt"), True)
        programming_file = models.ProgrammingFile.objects.create(
            file='learning_files/test12345.txt',
            title='test.txt',
            model=self.programming1_1
        )
        programming_file.delete_file()
        self.assertEqual(os.path.exists(settings.MEDIA_ROOT + "/learning_files/test12345.txt"), False)

    def test_module_file_delete(self):
        with open(settings.MEDIA_ROOT + "/learning_files/test12345.txt", "w+") as f:
            f.write('Test')
            f.close()
        self.assertEqual(os.path.exists(settings.MEDIA_ROOT + "/learning_files/test12345.txt"), True)
        module_file = models.ModuleFile.objects.create(
            file='learning_files/test12345.txt',
            title='test.txt',
            model=self.module1_1_1
        )
        module_file.delete_file()
        self.assertEqual(os.path.exists(settings.MEDIA_ROOT + "/learning_files/test12345.txt"), False)