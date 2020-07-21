import json
from urllib.parse import urlencode

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from circles import settings
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
        # Check data
        self.assertEqual(len(response.context['data']), self.visible_chapter_ct)
        self.assertEqual(len(response.context['data'][0]['sites']), self.visible_site_ct)
        self.assertEqual(len(response.context['data'][0]['sites'][0]['programming']), self.model_ct)
        self.assertEqual(len(response.context['data'][0]['sites'][0]['themes']), self.model_ct)
        self.assertEqual(len(response.context['data'][0]['sites'][0]['themes'][0]['modules']), self.model_ct)
        self.assertEqual(response.context['data'][0]['chapter'][0], 'chapter_access1')
        self.assertEqual(response.context['data'][0]['sites'][0]['site'][0], 'site_access1')
        self.assertEqual(response.context['data'][0]['sites'][0]['programming'][0][0], 'programming1')
        self.assertEqual(response.context['data'][0]['sites'][0]['themes'][0]['theme'][0], 'theme1')
        self.assertEqual(response.context['data'][0]['sites'][0]['themes'][0]['modules'][0][0], 'module1')

class TestLearningFiles(CreateLearningModelsMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')
        self.files_url = reverse('learning-files')
        self.create_learning_models()

    def test_upload_file(self):
        file = SimpleUploadedFile("media/default.jpg", b"file_content", content_type="image")
        request_data = {
            'model_type': 'programming',
            'model_pk': self.programming1_1.pk,
            'file': file,
        }
        response = self.client.post(self.files_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        data = json.loads(response.content)
        self.assertEqual(data['files'], [['file', 1, '/media/learning_files/default.jpg']])
        models.ProgrammingFile.objects.first().delete_file()

    def test_delete_file(self):
        with open(settings.MEDIA_ROOT + "/learning_files/test12345.txt", "w+") as f:
            f.write('Test')
            f.close()
        programming_file = models.ProgrammingFile.objects.create(
            file='learning_files/test12345.txt',
            title='test.txt',
            model=self.programming1_1
        )
        self.assertEqual(models.ProgrammingFile.objects.all().count(), 1)
        request_data = {
            'file_pk': 1,
            'model_type': 'programming',
        }
        response = self.client.post(self.files_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(models.ProgrammingFile.objects.all().count(), 0)
        with self.assertRaises(Exception):
            open(settings.MEDIA_ROOT + "/learning_files/test12345.txt")


class TestMembersCompleted(CreateLearningModelsMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')
        self.url = reverse('members-completed')
        self.create_learning_models()

    def test_GET_members_completed_theme(self):
        site = self.sites['site_access1']
        theme = self.theme1_1
        profile = site.profiles().first()
        models.ProfileTheme.objects.create(
            theme=theme,
            profile=profile,
            date_completed='1999-12-21'
        )
        models.ProfileTheme.objects.create(
            theme=theme,
            profile=profile,
        )
        request_data = {
            'model_type': 'theme',
            'pk': theme.pk,
        }
        response = self.client.get(self.url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        data = json.loads(response.content)
        profiles = json.loads(data['profiles'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]['name'], 'profile 1')

    def test_GET_members_completed_module(self):
        site = self.sites['site_access1']
        module = self.module1_1_1
        profile = site.profiles().first()
        models.ProfileModule.objects.create(
            module=module,
            profile=profile,
            date_completed='1999-12-21'
        )
        models.ProfileModule.objects.create(
            module=module,
            profile=profile,
        )
        request_data = {
            'model_type': 'module',
            'pk': module.pk,
        }
        response = self.client.get(self.url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        data = json.loads(response.content)
        profiles = json.loads(data['profiles'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]['name'], 'profile 1')

    def test_POST_members_completed_theme(self):
        theme = self.theme1_1
        profile = theme.site.profiles().first()
        request_data = {
            'model_type': 'theme',
            'pk': theme.pk,
            'profile_pk': profile.pk,
        }
        response = self.client.post(self.url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(theme.profiles.count(), 1)

    def test_POST_members_completed_theme_delete(self):
        theme = self.theme1_1
        profile = theme.site.profiles().first()
        models.ProfileTheme.objects.create(
            profile=profile,
            theme=theme,
        )
        self.assertEqual(theme.profiles.count(), 1)
        request_data = {
            'delete': True,
            'model_type': 'theme',
            'pk': theme.pk,
            'profile_pk': profile.pk,
        }
        response = self.client.post(self.url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(theme.profiles.count(), 0)

    def test_POST_members_completed_module(self):
        module = self.module1_1_1
        profile = module.site.profiles().first()
        request_data = {
            'model_type': 'module',
            'pk': module.pk,
            'profile_pk': profile.pk,
        }
        response = self.client.post(self.url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(module.profiles.count(), 1)

    def test_POST_members_completed_module_delete(self):
        module = self.module1_1_1
        profile = module.site.profiles().first()
        models.ProfileModule.objects.create(
            profile=profile,
            module=module,
        )
        self.assertEqual(module.profiles.count(), 1)
        request_data = {
            'delete': True,
            'model_type': 'module',
            'pk': module.pk,
            'profile_pk': profile.pk,
        }
        response = self.client.post(self.url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(module.profiles.count(), 0)


class TestLearningModelsView(CreateLearningModelsMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')
        self.models_url = reverse('learning-models')
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
        model = site.programming.first().facilitators_objects.first()
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

    def test_POST_create_model_programming(self):
        site = self.sites['site_access1']
        title = 'programming' + str(self.model_ct+2)
        form = urlencode({'description': 'Updated', 'title': title})
        request_data = {
            'model_type': 'programming',
            'form': form,
            'fields': 'description',
            'models': json.dumps([{'site':site.pk,}, ])
        }
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Programming.objects.filter(title=title).count(), 1)

    def test_POST_create_model_programming_no_access(self):
        site = self.sites['site_noaccess1']
        title = 'programming' + str(self.model_ct+2)
        form = urlencode({'description': 'Updated', 'title': title})
        request_data = {
            'model_type': 'programming',
            'form': form,
            'fields': 'description',
            'models': json.dumps([{'site':site.pk,}, ])
        }
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 403)

    def test_POST_update_model_programming_description(self):
        site = self.sites['site_access1']
        programming = self.programming1_1
        programming.links = '["google.com"]'
        programming.save()
        form = urlencode({'description': 'Updated', 'title': 'programming1', 'links': ''})
        request_data = {
            'model_type': 'programming',
            'form': form,
            'fields': 'description',
            'models': json.dumps([{'site':site.pk, 'pk': programming.pk}, ])
        }
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        programming = models.Programming.objects.get(pk=programming.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(programming.description, 'Updated')
        self.assertEqual(programming.links, '["google.com"]')

    def test_POST_update_model_programming_title_exists(self):
        site = self.sites['site_access1']
        programming = self.programming1_1
        replace_programming = self.programming1_2
        form = urlencode({'description': 'Updated', 'title': 'programming2'})
        request_data = {
            'model_type': 'programming',
            'form': form,
            'fields': 'description',
            'models': json.dumps([{'site':site.pk, 'pk': programming.pk, 'replace_pk': replace_programming.pk}, ])
        }
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        programming = models.Programming.objects.get(pk=programming.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(programming.title, 'programming2')
        self.assertEqual(site.programming.filter(title='programming2').count(), 1)

    def test_POST_update_model_programming_title_exists_unexpected(self):
        site = self.sites['site_access1']
        programming = self.programming1_1
        form = urlencode({'description': 'Updated', 'title': 'programming2'})
        request_data = {
            'model_type': 'programming',
            'form': form,
            'fields': 'description',
            'models': json.dumps([{'site':site.pk, 'pk': programming.pk}, ])
        }
        with self.assertRaises(ValidationError):
            self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_POST_create_model_theme(self):
        site = self.sites['site_access1']
        title = 'theme' + str(self.model_ct+2)
        form = urlencode({'title': title})
        request_data = {
            'model_type': 'theme',
            'form': form,
            'fields': 'all',
            'models': json.dumps([{'site':site.pk,}, ])
        }
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Theme.objects.filter(title=title).count(), 1)

    def test_POST_update_model_theme_title_exists(self):
        site = self.sites['site_access1']
        theme = self.theme1_1
        profile = site.profiles().first()
        models.ProfileTheme.objects.create(
            profile=profile,
            theme=theme,
        )
        self.assertEqual(theme.profiles.count(), 1)
        replace_theme = self.theme1_2
        profile = site.profiles().exclude(pk=profile.pk).first()
        models.ProfileTheme.objects.create(
            profile=profile,
            theme=replace_theme,
        )
        form = urlencode({'description': 'Updated', 'title': 'theme2'})
        request_data = {
            'model_type': 'theme',
            'form': form,
            'fields': 'all',
            'models': json.dumps([{'site':site.pk, 'pk': theme.pk, 'replace_pk': replace_theme.pk}, ])
        }
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        theme = models.Theme.objects.get(pk=theme.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(theme.title, 'theme2')
        self.assertEqual(site.themes.filter(title='theme2').count(), 1)
        self.assertEqual(theme.profiles.count(), 2)

    def test_POST_update_model_theme_title_exists_unexpected(self):
        site = self.sites['site_access1']
        theme = self.theme1_1
        form = urlencode({'description': 'Updated', 'title': 'theme2'})
        request_data = {
            'model_type': 'theme',
            'form': form,
            'fields': 'description',
            'models': json.dumps([{'site':site.pk, 'pk': theme.pk}, ])
        }
        with self.assertRaises(ValidationError):
            self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_POST_create_model_module(self):
        site = self.sites['site_access1']
        title = 'module' + str(self.model_ct+2)
        form = urlencode({'description': 'Updated', 'title': title})
        request_data = {
            'model_type': 'module',
            'form': form,
            'fields': 'description',
            'models': json.dumps([{'site':site.pk, 'theme':'new_theme'}, ])
        }
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(models.Module.objects.filter(title=title).count(), 1)
        self.assertEqual(models.Theme.objects.filter(title='new_theme').count(), 1)

    def test_POST_update_model_module(self):
        site = self.sites['site_access1']
        programming = self.programming1_1
        form = urlencode({'description': 'Updated', 'title': 'programming1'})
        request_data = {
            'model_type': 'programming',
            'form': form,
            'fields': 'description',
            'models': json.dumps([{'site':site.pk, 'pk': programming.pk}, ])
        }
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        programming = models.Programming.objects.get(pk=programming.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(programming.description, 'Updated')

    def test_POST_update_model_module_title_exists(self):
        site = self.sites['site_access1']
        theme = self.theme1_1
        module = self.module1_1_1
        profile = site.profiles().first()
        models.ProfileModule.objects.create(
            profile=profile,
            module=module,
        )
        self.assertEqual(module.profiles.count(), 1)
        self.assertEqual(module.facilitators_objects.count(), 1)
        module.facilitators = '["John Doe"]'
        replace_module = self.module1_1_2
        profile = site.profiles().exclude(pk=profile.pk).first()
        models.ProfileModule.objects.create(
            profile=profile,
            module=replace_module,
        )
        replace_module.facilitators_objects.add(members_models.Profile.objects.get(pk=2))
        replace_module.facilitators = '["Sally Shoe"]'
        self.assertEqual(replace_module.profiles.count(), 1)
        self.assertEqual(replace_module.facilitators_objects.count(), 2)
        module.save()
        replace_module.save()
        form = urlencode({'description': 'Updated', 'title': 'module2'})
        request_data = {
            'model_type': 'module',
            'form': form,
            'fields': 'description',
            'models': json.dumps([{'site':site.pk,'theme':theme.title, 'pk': module.pk, 'replace_pk': replace_module.pk}, ])
        }
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        module = models.Module.objects.get(pk=module.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(module.title, 'module2')
        self.assertEqual(theme.modules.filter(title='module2').count(), 1)
        self.assertEqual(module.profiles.count(), 2)
        self.assertEqual(module.facilitators, '["John Doe", "Sally Shoe"]')
        self.assertEqual(module.facilitators_objects.count(), 2)

    def test_POST_update_model_module_title_exists_unexpected(self):
        site = self.sites['site_access1']
        module = self.module1_1_1
        form = urlencode({'description': 'Updated', 'title': 'module2'})
        request_data = {
            'model_type': 'module',
            'form': form,
            'fields': 'description',
            'models': json.dumps([{'site':site.pk, 'theme': 'theme1', 'pk': module.pk}, ])
        }
        with self.assertRaises(ValidationError):
            self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    def test_POST_delete_programming(self):
        request_data = {
            'delete': True,
            'model_type': 'programming',
            'models': json.dumps([{'pk': self.programming1_1.pk}]),
        }
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(self.sites['site_access1'].programming.filter(
            title='programming1').count(), 0)

    def test_POST_delete_programming_no_access(self):
        programming = self.sites['site_noaccess1'].programming.get(title='programming1')
        request_data = {
            'delete': True,
            'model_type': 'programming',
            'models': json.dumps([{'pk': programming.pk}]),
        }
        response = self.client.post(self.models_url, request_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 403)
