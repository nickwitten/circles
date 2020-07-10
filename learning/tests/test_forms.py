from django.contrib.auth.models import User
from django.test import TestCase

from learning.forms import ProgrammingCreationForm, ModuleCreationForm
from learning.tests.test_models import CreateLearningModelsMixin


class TestForms(CreateLearningModelsMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='password')
        self.create_learning_models()

    def test_form_required_fields(self):
        form = ProgrammingCreationForm()
        self.assertEqual(form.required_fields, ['title'])

    def test_form_save(self):
        form_data = {'title': 'PROGRAM'}
        form = ModuleCreationForm(form_data)
        attrs = {'site': self.sites['site_access1'], 'theme': self.theme1_1}
        module = form.save(**attrs)
        self.assertEqual(module.site, self.sites['site_access1'])
        self.assertEqual(module.theme, self.theme1_1)
