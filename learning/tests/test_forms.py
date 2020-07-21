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

    def test_form_save_keywords(self):
        form_data = {'title': 'PROGRAM'}
        form = ModuleCreationForm(form_data)
        attrs = {'site': self.sites['site_access1'], 'theme': self.theme1_1}
        if form.is_valid():
            module = form.save(**attrs)
        self.assertEqual(module.site, self.sites['site_access1'])
        self.assertEqual(module.theme, self.theme1_1)

    def test_form_save_facilitators(self):
        site = self.sites['site_access1']
        facilitator_profile = site.profiles().first()
        form_data = {
            'title': 'PROGRAM',
            'facilitators': '["John Doe", {"pk": ' + str(facilitator_profile.pk) + ', "name": "profile 1"}]'
        }
        attrs = {'site': site, 'theme': self.theme1_1}
        form = ModuleCreationForm(form_data)
        if form.is_valid():
            module = form.save(**attrs)
        self.assertEqual(module.facilitators_objects.first(), facilitator_profile)
        self.assertEqual(module.facilitators, '["John Doe"]')

    def test_form_save_facilitator_pk_not_in_site(self):
        site = self.sites['site_access1']
        facilitator_profile = self.sites['site_noaccess1'].profiles().first()
        form_data = {
            'title': 'PROGRAM',
            'facilitators': '["John Doe", {"pk": ' + str(facilitator_profile.pk) + ', "name": "profile 1"}]'
        }
        attrs = {'site': site, 'theme': self.theme1_1}
        form = ModuleCreationForm(form_data)
        if form.is_valid():
            module = form.save(**attrs)
        self.assertEqual(module.facilitators_objects.count(), 0)
        self.assertEqual(module.facilitators, '["John Doe"]')
