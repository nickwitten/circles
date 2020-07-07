import json
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from members import models as members_models
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

    def test_GET_no_data(self):
        # No data given should 404
        self.client.raise_request_exception = False
        request_data = {}
        with self.assertRaises(ValidationError):
            self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_GET_model_info(self):
        # Should return model info
        for related, model_type in self.model_types:
            model = getattr(self.sites['site_access1'], related).first()
            request_data = {'pk': str(model.pk),'model_type': model_type}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content), model.to_dict())

    def test_GET_model_info_no_access(self):
        # Outside of access sites should 404
        for related, model_type in self.model_types:
            model = getattr(self.sites['site_noaccess1'], related).first()
            request_data = {'pk': str(model.pk),'model_type': model_type}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 403)

    def test_GET_model_info_invalid_pk(self):
        # Invalid pk should 404
        for related, model_type in self.model_types:
            request_data = {'pk': str(100000),'model_type': model_type}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 404)

    def test_GET_model_info_no_type(self):
        # Pk with no type should 404
        pk = self.sites['site_access1'].programming.first().pk
        request_data = {'pk': str(pk)}
        with self.assertRaises(ValidationError):
            self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_GET_autocomplete(self):
        # Autocomplete learning models
        for related, model_type in self.model_types:
            model = getattr(self.sites['site_access1'], related).first()
            search = model.title[:-1]
            request_data = {'model_type': model_type, 'autocomplete_search': search}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 200)
            self.assertCountEqual(json.loads(response.content)['results'],
                                  [model_type+str(i+1) for i in range(self.model_ct)])

    def test_GET_autocomplete_no_results(self):
        # No results
        for related, model_type in self.model_types:
            model = getattr(self.sites['site_access1'], related).first()
            search = 'xyz123'
            request_data = {'model_type': model_type, 'autocomplete_search': search}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 200)
            self.assertCountEqual(json.loads(response.content)['results'], [])

    def test_GET_autocomplete_no_modeltype(self):
        # Autocomplete without modeltype should 404
        request_data = {'autocomplete_search': 'programming'}
        with self.assertRaises(ValidationError):
            self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_GET_autocomplete_invalid_modeltype(self):
        # Autocomplete with invalid modeltype should 404
        request_data = {'model_type': 'facilitator', 'autocomplete_search': 'programming'}
        with self.assertRaises(ValidationError):
            self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_GET_autocomplete_no_search(self):
        # No search input should 404
        for related, model_type in self.model_types:
            model = getattr(self.sites['site_access1'], related).first()
            search = ''
            request_data = {'model_type': model_type, 'autocomplete_search': search}
            with self.assertRaises(ValidationError):
                self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_GET_autocomplete_facilitators(self):
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

    def test_GET_autocomplete_facilitators_no_results(self):
        # No results
        site = self.sites['site_access1']
        search = 'xyz123'
        request_data = {'autocomplete_facilitator_search': search, 'site_pk': site.pk}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(json.loads(response.content)['results'],
                              [])

    def test_GET_autocomplete_facilitators_site_no_access(self):
        # Should raise 404 because we don't have access to this site
        site = self.sites['site_noaccess1']
        search = 'xyz123'
        request_data = {'autocomplete_facilitator_search': search, 'site_pk': site.pk}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 403)

    def test_GET_autocomplete_facilitators_no_site(self):
        # No site raise 404
        search = 'xyz123'
        request_data = {'autocomplete_facilitator_search': search}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 404)

    def test_GET_autocomplete_facilitators_invalid_site(self):
        # invalid site raise 404
        search = 'xyz123'
        request_data = {'autocomplete_facilitator_search': search, 'site_pk': 10000}
        response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 404)

    def test_GET_check_existing(self):
        # Search with model identifiers.  This test queries all sites with access.
        # Return [{site: pk, model: pk}, ]
        for related, model_type in self.model_types:
            sites = list(self.user.userinfo.user_site_access().values_list('pk', flat=True))
            search = model_type + '1'
            request_data = {'check_existing':True, 'sites': json.dumps(sites), 'model_type': model_type, 'title': search}
            if model_type == 'module':
                request_data['theme'] = 'theme1'
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            results = []
            sites = self.user.userinfo.user_site_access()
            for site in sites:
                result = {}
                model = getattr(site, related).filter(title=search).first()
                result['site'] = site.pk
                if model_type == 'module':
                    result['theme'] = 'theme1'
                result['model'] = model.pk
                results.append(result)
            self.assertEqual(response.status_code, 200)
            self.assertCountEqual(json.loads(response.content)['results'], results)

    def test_GET_check_existing_module_insufficient_kwargs(self):
        # Should 404 because required data was popped
        for key in ['sites', 'model_type', 'title']:
            for related, model_type in self.model_types:
                sites = list(self.user.userinfo.user_site_access().values_list('pk', flat=True))
                search = model_type + '1'
                request_data = {'check_existing': True, 'sites': json.dumps(sites), 'model_type': model_type,
                                'title': search}
                if model_type == 'module':
                    request_data['theme'] = 'theme1'
                request_data.pop(key)
                with self.assertRaises(ValidationError):
                    response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_GET_check_existing_no_sites(self):
        # Should return empty list
        for related, model_type in self.model_types:
            search = model_type + '1'
            request_data = {'check_existing': True, 'sites': json.dumps([]), 'model_type': model_type,
                            'title': search, 'theme': 'theme1'}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertCountEqual(json.loads(response.content)['results'], [])

    def test_GET_check_existing_no_site_access(self):
        # Should return empty list
        for related, model_type in self.model_types:
            sites = [self.sites['site_noaccess1'].pk, ]
            search = model_type + '1'
            request_data = {'check_existing': True, 'sites': json.dumps(sites), 'model_type': model_type,
                            'title': search, 'theme': 'theme1'}
            response = self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertCountEqual(json.loads(response.content)['results'], [])

    def test_GET_check_existing_module_no_theme(self):
        # Should return empty list
        model_type = 'module'
        search = model_type + '1'
        request_data = {'check_existing': True, 'sites': json.dumps([]), 'model_type': model_type, 'title': search}
        with self.assertRaises(ValidationError):
            self.client.get(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_POST_update_models_programming(self):
        # Should update programming 1 in each site and create if not there
        title = 'programming1'
        sites = self.user.userinfo.user_site_access()
        models = []
        # Delete to check if it's added
        self.sites['site_access1'].programming.get(title=title).delete()
        for site in sites:
            model = site.programming.filter(title=title).first()
            model_info = {'site': site.pk}
            if model:
                model_info['pk'] = model.pk
            models.append(model_info)
        form_data = {'description': 'Updated', 'title': title}
        form_data = urlencode(form_data)
        request_data = {
            'model_type': 'programming', 'models': json.dumps(models), 'form': form_data, 'fields': 'all'}
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        # model was added back
        self.assertIsNotNone(self.sites['site_access1'].programming.get(title=title))
        # models are updated
        self.assertEqual(self.sites['site_access1'].programming.get(title=title).description, 'Updated')
        self.assertEqual(self.sites['site_access2'].programming.get(title=title).description, 'Updated')

    def test_POST_update_models_programming_title(self):
        # Should update programming1 to unused title in each site
        title = 'programming1'
        update_title = 'programming' + str(self.model_ct+2)
        sites = self.user.userinfo.user_site_access()
        models = []
        for site in sites:
            model = site.programming.get(title=title)
            model_info = {'site': site.pk, 'title': title}
            if model:
                model_info['pk'] = model.pk
            models.append(model_info)
        form_data = {'description': 'Updated', 'title': update_title}
        form_data = urlencode(form_data)
        request_data = {'model_type': 'programming', 'models': json.dumps(models), 'form': form_data}
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        # model was changed
        self.assertEqual(self.sites['site_access1'].programming.filter(title=title).count(), 0)
        # models are updated
        self.assertEqual(self.sites['site_access1'].programming.filter(title=update_title).count(), 1)

    def test_POST_update_models_theme_title(self):
        # Should update theme1 to unused title in each site
        title = 'theme1'
        update_title = 'theme' + str(self.model_ct+2)
        sites = self.user.userinfo.user_site_access()
        models = []
        for site in sites:
            model = site.themes.get(title=title)
            model_info = {'site': site.pk, 'title': title}
            if model:
                model_info['pk'] = model.pk
            models.append(model_info)
        form_data = {'title': update_title}
        form_data = urlencode(form_data)
        request_data = {'model_type': 'theme', 'models': json.dumps(models), 'form': form_data}
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        # model was changed
        self.assertEqual(self.sites['site_access1'].themes.filter(title=title).count(), 0)
        # models are updated
        self.assertEqual(self.sites['site_access1'].themes.filter(title=update_title).count(), 1)

    def test_POST_update_models_module(self):
        # Should update module1 in each theme and create if not there
        title = 'module1'
        sites = self.user.userinfo.user_site_access()
        models = []
        # Delete to check if it's added
        self.sites['site_access1'].modules.get(theme__title='theme1',title=title).delete()
        for site in sites:
            for theme in site.themes.all():
                model = theme.modules.filter(title=title).first()
                model_info = {'site': site.pk, 'theme': theme.pk, 'title': title}
                if model:
                    model_info['pk'] = model.pk
                models.append(model_info)
        form_data = {'description': 'Updated', 'title': title}
        form_data = urlencode(form_data)
        request_data = {'model_type': 'module', 'models': json.dumps(models), 'form': form_data}
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        # model was added back
        self.assertEqual(self.sites['site_access1'].modules.filter(theme__title='theme1', title=title).count(), 1)
        # models are updated
        self.assertEqual(self.sites['site_access2'].modules.first().description, 'Updated')

    def test_POST_update_models_module_title(self):
        # Should update theme1 to unused title in each site
        title = 'module1'
        update_title = 'module' + str(self.model_ct+2)
        sites = self.user.userinfo.user_site_access()
        models = []
        for site in sites:
            for theme in site.themes.all():
                model = theme.modules.filter(title=title).first()
                model_info = {'site': site.pk, 'theme': theme.pk, 'title': title}
                if model:
                    model_info['pk'] = model.pk
                models.append(model_info)
        form_data = {'title': update_title}
        form_data = urlencode(form_data)
        request_data = {'model_type': 'module', 'models': json.dumps(models), 'form': form_data}
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        # models were changed
        self.assertEqual(self.sites['site_access1'].modules.filter(title=title).count(), 0)
        self.assertNotEqual(self.sites['site_access1'].modules.filter(title=update_title).count(), 0)

    def test_POST_update_models_module_title_existing_title(self):
        site = self.sites['site_access1']
        theme = site.themes.first()
        model = theme.modules.get(title='module1')
        replace_model = theme.modules.get(title='module2')
        form_data = {'title':'module2'}
        models = [{
            'site': site.pk,
            'theme': theme.pk,
            'title': 'module1',
            'pk': model.pk,
            'replace_pk': replace_model.pk
        }, ]
        request_data = {'model_type': 'module', 'models': json.dumps(models), 'form': urlencode(form_data)}
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(theme.modules.get(title='module2').pk, model.pk)

    def test_POST_update_models_module_title_existing_title_no_pk(self):
        form_data = {'title':'module2'}
        site = self.sites['site_access1']
        models = [{
            'site': site.pk,
            'theme': site.themes.first().pk,
            'title': 'module1',
        }, ]
        request_data = {'model_type': 'module', 'models': json.dumps(models), 'form': urlencode(form_data)}
        with self.assertRaises(ValidationError):
            self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_POST_update_models_missing_args(self):
        args = ['model_type', 'models', 'form', 'site', 'theme', 'title', 'pk']
        for arg in args:
            title = 'theme1'
            update_title = 'theme' + str(self.model_ct+2)
            sites = self.user.userinfo.user_site_access()
            models = []
            for site in sites:
                for theme in site.themes.all():
                    model = theme.modules.filter(title=title).first()
                    model_info = {'site': site.pk, 'theme': theme.pk, 'title': title}
                    if model:
                        model_info['pk'] = model.pk
                    model_info.pop(arg, None)
                    models.append(model_info)
            form_data = {'title': update_title}
            form_data = urlencode(form_data)
            request_data = {'model_type': 'theme', 'models': json.dumps(models), 'form': form_data}
            request_data.pop(arg, None)
            with self.assertRaises(ValidationError):
                self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_POST_update_models_no_site_access(self):
        title = 'theme1'
        update_title = 'theme' + str(self.model_ct+2)
        sites = [self.sites['site_noaccess1']]
        models = []
        for site in sites:
            for theme in site.themes.all():
                model = theme.modules.filter(title=title).first()
                model_info = {'site': site.pk, 'theme': theme.pk, 'title': title}
                if model:
                    model_info['pk'] = model.pk
                models.append(model_info)
        form_data = {'title': update_title}
        form_data = urlencode(form_data)
        request_data = {'model_type': 'theme', 'models': json.dumps(models), 'form': form_data}
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 403)
