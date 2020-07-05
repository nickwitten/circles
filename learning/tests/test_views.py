import json

from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.test import TestCase, Client
from django.urls import reverse
from members import models as members_models
from members.tests.test_models import CreateChaptersMixin
from learning.tests.test_models import CreateLearningModelsMixin
from learning import forms, models


class TestLearningView(CreateLearningModelsMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')
        self.learning_url = reverse('learning')

    def test_learning_GET(self):
        self.create_learning_models()
        response = self.client.get(self.learning_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'learning/learning.html')
        # Check chapter_info
        self.assertEqual(len(response.context['chapter_info']), self.visible_chapter_ct)
        self.assertEqual(len(response.context['chapter_info'][0]['sites']), self.visible_site_ct)
        self.assertEqual(len(response.context['chapter_info'][0]['sites'][0]['programming']), self.model_ct)
        self.assertEqual(len(response.context['chapter_info'][0]['sites'][0]['themes']), self.model_ct)
        self.assertEqual(len(response.context['chapter_info'][0]['sites'][0]['themes'][0]['modules']), self.model_ct)
        self.assertEqual(response.context['chapter_info'][0]['chapter'], self.chapters['chapter_access1'])
        self.assertEqual(response.context['chapter_info'][0]['sites'][0]['site'], self.sites['site_access1'])
        self.assertEqual(response.context['chapter_info'][0]['sites'][0]['programming'][0].title, 'programming1')
        self.assertEqual(response.context['chapter_info'][0]['sites'][0]['themes'][0]['theme'].title, 'theme1')
        self.assertEqual(response.context['chapter_info'][0]['sites'][0]['themes'][0]['modules'][0].title, 'module1')


class TestLearningModelsView(CreateLearningModelsMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')
        self.models_url = reverse('models')
        self.create_learning_models()
        self.model_types = [('programming', 'programming'), ('themes', 'theme'), ('modules', 'module')]

    def test_learning_models_GET_no_data(self):
        # No data given should 404
        request_data = {}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 404)

    def test_learning_models_GET_model_info(self):
        # Should return model info
        for related, model_type in self.model_types:
            model = getattr(self.sites['site_access1'], related).first()
            request_data = {'pk': str(model.pk),'model_type': model_type}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content), model.to_dict())

    def test_learning_models_GET_model_info_no_access(self):
        # Outside of access sites should 404
        for related, model_type in self.model_types:
            model = getattr(self.sites['site_noaccess1'], related).first()
            request_data = {'pk': str(model.pk),'model_type': model_type}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 404)

    def test_learning_models_GET_model_info_invalid_pk(self):
        # Invalid pk should 404
        for related, model_type in self.model_types:
            request_data = {'pk': str(100000),'model_type': model_type}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 404)

    def test_learning_models_GET_model_info_no_type(self):
        # Pk with no type should 404
        pk = self.sites['site_access1'].programming.first().pk
        request_data = {'pk': str(pk)}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 404)

    def test_learning_models_GET_autocomplete(self):
        # Autocomplete learning models
        for related, model_type in self.model_types:
            model = getattr(self.sites['site_access1'], related).first()
            search = model.title[:-1]
            request_data = {'model_type': model_type, 'autocomplete_search': search}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 200)
            self.assertCountEqual(json.loads(response.content)['results'],
                                  [model_type+str(i+1) for i in range(self.model_ct)])

    def test_learning_models_GET_autocomplete_no_results(self):
        # No results
        for related, model_type in self.model_types:
            model = getattr(self.sites['site_access1'], related).first()
            search = 'xyz123'
            request_data = {'model_type': model_type, 'autocomplete_search': search}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 200)
            self.assertCountEqual(json.loads(response.content)['results'], [])

    def test_learning_models_GET_autocomplete_no_modeltype(self):
        # Autocomplete without modeltype should 404
        request_data = {'autocomplete_search': 'programming'}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 404)

    def test_learning_models_GET_autocomplete_invalid_modeltype(self):
        # Autocomplete with invalid modeltype should 404
        request_data = {'model_type': 'facilitator', 'autocomplete_search': 'programming'}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 404)

    def test_learning_models_GET_autocomplete_no_search(self):
        # No search input should 404
        for related, model_type in self.model_types:
            model = getattr(self.sites['site_access1'], related).first()
            search = ''
            request_data = {'model_type': model_type, 'autocomplete_search': search}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 404)

    def test_learning_models_GET_autocomplete_facilitators(self):
        # Autocomplete facilitator field with profiles in current site
        site = self.sites['site_access1']
        model = site.programming.first().facilitator_profiles.first()
        search = model.first_name
        result = site.profiles()
        request_data = {'autocomplete_facilitator_search': search, 'site_pk': site.pk}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(json.loads(response.content)['results'],
                              [[str(profile), profile.pk] for profile in result])

    def test_learning_models_GET_autocomplete_facilitators_no_results(self):
        # No results
        site = self.sites['site_access1']
        search = 'xyz123'
        request_data = {'autocomplete_facilitator_search': search, 'site_pk': site.pk}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(json.loads(response.content)['results'],
                              [])

    def test_learning_models_GET_autocomplete_facilitators_site_no_access(self):
        # Should raise 404 because we don't have access to this site
        site = self.sites['site_noaccess1']
        search = 'xyz123'
        request_data = {'autocomplete_facilitator_search': search, 'site_pk': site.pk}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 404)

    def test_learning_models_GET_autocomplete_facilitators_no_site(self):
        # No site raise 404
        search = 'xyz123'
        request_data = {'autocomplete_facilitator_search': search}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 404)

    def test_learning_models_GET_autocomplete_facilitators_invalid_site(self):
        # invalid site raise 404
        search = 'xyz123'
        request_data = {'autocomplete_facilitator_search': search, 'site_pk': 10000}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 404)
