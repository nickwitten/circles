import json
from django.db.models import Value
from django.db import models as django_models
from django.db.models.functions import Concat
from django.http import Http404, HttpResponseServerError, JsonResponse, QueryDict
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView, View, ContextMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
import members.models as member_models
from circles import settings
from . import forms, models
from django.core.exceptions import PermissionDenied, ValidationError


class AjaxMixin:

    def setup(self, request, *args, **kwargs):
        data = dict(getattr(request, 'GET', None) or getattr(request, 'POST', None))
        data = dict([(key, value[0]) for key, value in data.items()])
        kwargs.update(data)
        super().setup(request, *args, **kwargs)


class Learning(TemplateView):
    template_name = 'learning/learning.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['positions'] = member_models.Role.position_choices
        context['forms'] = [
            ('programming', forms.ProgrammingCreationForm(auto_id="programming_%s")),
            ('theme', forms.ThemeCreationForm(auto_id="theme_%s")),
            ('module', forms.ModuleCreationForm(auto_id="module_%s")),
        ]
        data = self.get_data()
        context['data'] = data
        return context

    def get_data(self):
        chapters = self.request.user.userinfo.user_site_access_dict()
        data = []
        for chapter in chapters:
            temp_chapter = {
                'chapter': (str(chapter['chapter']), chapter['chapter'].pk),
                'sites': [],
            }
            sites = chapter['sites']
            for site in sites:
                temp_site = {
                    'site': (str(site), site.pk),
                    'programming': [(str(programming), programming.pk) for programming in site.programming.all()],
                    'themes': [],
                }
                themes = site.themes.all()
                for theme in themes:
                    temp_theme = {
                        'theme': (str(theme), theme.pk),
                        'modules': []
                    }
                    for module in theme.modules.all():
                        try:
                            required_for = json.loads(module.required_for)
                        except:
                            required_for = []
                        temp_module = (str(module), module.pk, required_for)
                        temp_theme['modules'] += [temp_module]
                    temp_site['themes'] += [temp_theme]
                temp_chapter['sites'] += [temp_site]
            data += [temp_chapter]
        return data


class LearningModels(LoginRequiredMixin, AjaxMixin, View):
    data = {}
    # Hash to (class, related_name, form_class)
    models = {
        'programming': (models.Programming, 'programming', forms.ProgrammingCreationForm),
        'theme': (models.Theme, 'themes', forms.ThemeCreationForm),
        'module': (models.Module, 'modules', forms.ModuleCreationForm),
    }

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('pk'):
            self.get_model_info()
        elif self.kwargs.get('check_existing'):
            self.check_existing()
        elif self.kwargs.get('autocomplete_search'):
            self.autocomplete()
        elif self.kwargs.get('autocomplete_facilitator_search'):
            self.autocomplete_facilitator()
        else:
            raise ValidationError('No Operation', code=500)
        return JsonResponse(self.data)

    def post(self, request, *args, **kwargs):
        if self.kwargs.get('delete'):
            self.delete_model()
        else:
            self.create_or_update_models()
        return JsonResponse(self.data)

    def get_model_info(self):
        """ Gets dictionary of model information if the user has access. """
        pk = self.kwargs['pk']
        model_type = self.models.get(self.kwargs.get('model_type'))
        if not (model_type and pk):
            raise ValidationError('Insufficient Data')
        model = get_object_or_404(model_type[0], pk=pk)
        if model.site not in self.request.user.userinfo.user_site_access():
            raise PermissionDenied()
        self.data = model.to_dict()

    def check_existing(self):
        """ Gets existing models in each site """
        sites = self.kwargs.get('sites')
        model_type = self.models.get(self.kwargs.get('model_type'))
        title = self.kwargs.get('title')
        theme = None
        if not (sites and model_type and title):
            raise ValidationError('Insufficient Data', code=500)
        if model_type[0] == models.Module:
            theme = self.kwargs.get('theme')
            if not theme:
                raise ValidationError('Theme Required for Module', code=500)
        results = []
        sites = self.request.user.userinfo.user_site_access().filter(pk__in=json.loads(sites))
        for site in sites:
            queryset = getattr(site, model_type[1]).filter(title=title)
            if theme:
                queryset = queryset.filter(theme__title=theme)
            if queryset.count() > 1:
                raise ValidationError('Duplicate Learning Models', code=500)
            if queryset.count() < 1:
                continue
            model = queryset.first()
            result = {'site': site.pk, 'model': model.pk}
            if theme:
                result['theme'] = theme
            results.append(result)
        self.data['results'] = results

    def autocomplete(self):
        """" Gets names of similar models even without site access """
        search = self.kwargs['autocomplete_search']
        model_type = self.models.get(self.kwargs.get('model_type'))
        if not (search and model_type):
            raise ValidationError('Insufficient Data', code=500)
        results = list(model_type[0].objects.filter(title__icontains=search).values_list(
                        'title', flat=True))
        # Sort by frequency
        results = sorted(results, key=results.count, reverse=True)
        # Get distinct while maintaining order
        seen = set()
        seen_add = seen.add
        results = [x for x in results if not (x in seen or seen_add(x))]
        self.data = {'results': results}

    def autocomplete_facilitator(self):
        """ Gets profiles from current site that autocomplete search """
        search = self.kwargs['autocomplete_facilitator_search']
        site = get_object_or_404(member_models.Site, pk=self.kwargs.get('site_pk'))
        if site not in self.request.user.userinfo.user_site_access():
            raise PermissionDenied()
        results = member_models.Profile.objects.filter(roles__site=site)
        results = results.annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
        results = results.filter(fullname__icontains=search).values_list('first_name', 'last_name', 'pk')
        results = set(results)
        results = [[match[0] + ' ' + match[1], match[2]] for match in results]
        self.data = {'results': results}

    def delete_model(self):
        """ Takes {site, (theme), pk} objects and deletes """
        model_type = self.models.get(self.kwargs.get('model_type'))
        models = self.kwargs.get('models')
        if not (models and model_type):
            raise ValidationError('Insufficient Data')
        models = json.loads(models)
        for model in models:
            pk = model.get('pk')
            model = get_object_or_404(model_type[0], pk=pk)
            if model.site not in self.request.user.userinfo.user_site_access():
                raise PermissionDenied()
            if hasattr(model, 'files'):
                for file in model.files.all():
                    file.delete_file()
            model.delete()

    def create_or_update_models(self):
        """ Takes {site, (theme), (pk)} objects for each
            model that needs to be updated or created.  Theme
            required if model is module.  Pk required if model
            already exists.                                     """
        model_type, form_data, model_infos = self._get_args()
        models = []
        for info in model_infos:
            attrs, pk, replace_pk = self._get_model_info(model_type, info)
            if pk:
                models += [self._update_model(model_type, attrs, pk,
                                   replace_pk, form_data)]
            else:
                models += [self._create_model(model_type, attrs, form_data)]
        # Commit changes
        for model in models:
            model.save()

    def _get_args(self):
        """ Process create_or_update_models args """
        model_type = self.models.get(self.kwargs.get('model_type'))
        form_data = self.kwargs.get('form')
        form_fields = self.kwargs.get('fields')
        model_infos = self.kwargs.get('models')
        if not (model_type and form_data and form_fields and model_infos):
            raise ValidationError('Insufficient Data', code=500)
        form_data = QueryDict(form_data).copy()
        # Only edit specified fields
        if form_fields != 'all':
            ignore_fields = []
            for field in form_data.keys():
                if field in model_type[2]().required_fields:
                    continue
                if field not in form_fields:
                    ignore_fields.append(field)
            for field in ignore_fields:
                form_data.pop(field)
        model_infos = json.loads(model_infos)
        return model_type, form_data, model_infos

    def _get_model_info(self, model_type, info):
        """ Unpack and validate model info. Target
            values not current values.
            INPUTS:
            Site       - pk of model's site
            Theme      - title of target theme if
                         modeltype is module
            pk         - pk of model to be updated
            replace_pk - pk of model with target info """
        site = info.get('site')
        theme = info.get('theme')
        pk = info.get('pk')
        replace_pk = info.get('replace_pk')
        site = get_object_or_404(member_models.Site, pk=site)
        if site not in self.request.user.userinfo.user_site_access():
            raise PermissionDenied('Access Denied')
        attrs = {'site': site}
        if model_type[0] == models.Module:
            if not theme:
                raise ValidationError('Module Requires Theme Title')
            temp_theme = models.Theme.objects.filter(title=theme, **attrs).first()
            # Theme doesn't exist in this site so create
            if not temp_theme:
                temp_theme = models.Theme.objects.create(title=theme, **attrs)
            theme = temp_theme
            if theme.site != site:
                raise ValidationError('Theme Site Does Not Match Module Site', code=500)
            attrs['theme'] = theme
        return attrs, pk, replace_pk

    def _update_model(self, model_type, attrs, pk, replace_pk, form_data):
        """ Update model.  If model info exists,
            replace it and merge some fields    """
        model = get_object_or_404(model_type[0], pk=pk)
        if model.site not in self.request.user.userinfo.user_site_access():
            raise PermissionDenied('Access Denied')
        form = model_type[2](form_data, instance=model)
        if form.is_valid():
            model = self._check_and_replace(model_type, form,
                                               attrs, pk, replace_pk)
            # If replaced model save was handled
            if not model:
                model = form.save(commit=False, **attrs)
            return model
        else:
            raise ValidationError('Invalid Form')

    def _check_and_replace(self, model_type, form, attrs, pk, replace_pk):
        """ Check if model needs to be replaced and
            if that was expected.  Merge fields from
            replaced model and then delete.          """
        # Check for models with same info
        replace = model_type[0].objects.filter(
            title=form.cleaned_data['title'], **attrs
        ).exclude(pk=pk).first()
        if replace:
            # Validate user meant to replace
            if replace_pk != replace.pk:
                raise ValidationError('Unexpected Replacement')
            model = form.save(commit=False, **attrs)
            # Merge specified fields
            for field in model_type[2].merge_fields:
                if hasattr(replace, field):
                    field_type = model_type[0]._meta.get_field(
                        field).get_internal_type()
                    if field_type == 'ManyToManyField':
                        for related in getattr(replace, field).all():
                            getattr(model, field).add(related)
                    elif field_type == 'ForeignKey':
                        for related in getattr(replace, field).all():
                            setattr(related, self.kwargs.get('model_type'), model)
                            related.save()
                    elif field_type == 'TextField':
                        try:
                            replace_objs = json.loads(getattr(replace, field))
                            model_objs = json.loads(getattr(model, field))
                            for obj in replace_objs:
                                model_objs += [obj]
                            setattr(model, field, json.dumps(model_objs))
                        except Exception:
                            pass
                if hasattr(replace, 'files'):
                    for file in replace.files.all():
                        file.delete_file()
            replace.delete()
            return model
        return False

    @staticmethod
    def _create_model(model_type, attrs, form_data):
        form = model_type[2](form_data)
        if form.is_valid():
            # Verify that no model with this info exists
            if model_type[0].objects.filter(title=form.cleaned_data['title'], **attrs):
                raise ValidationError('Model Already Exists ID Required', code=500)
            return form.save(commit=False, **attrs)
        else:
            raise ValidationError('Invalid Form')


class LearningFiles(LoginRequiredMixin, AjaxMixin, View):
    models = {
        'programming': (models.Programming, models.ProgrammingFile),
        'module': (models.Module, models.ModuleFile),
    }
    data = {}

    def post(self, request):
        context = {}
        if self.kwargs.get('file_pk'):
            self.delete_learning_file()
            pass
        else:
            self.create_learning_file()
        return JsonResponse(self.data)

    def create_learning_file(self):
        model_type = self.models.get(self.kwargs.get('model_type'))
        model_pk = self.kwargs.get('model_pk')
        if not (model_type and model_pk):
            raise ValidationError('Insufficient Data')
        model = get_object_or_404(model_type[0], pk=model_pk)
        if model.site not in self.request.user.userinfo.user_site_access():
            raise PermissionDenied()
        files = self.request.FILES
        created_files = []
        for title, file in files.items():
            learning_file = model_type[1](model=model, file=file, title=title)
            learning_file.save()
            created_files += [(title, learning_file.pk, settings.MEDIA_URL + learning_file.file.name)]
        self.data = {
            'files': created_files
        }

    def delete_learning_file(self):
        pk = self.kwargs.get('file_pk')
        model_type = self.models.get(self.kwargs.get('model_type'))
        if not model_type:
            raise ValidationError('Insufficient Data')
        learning_file = get_object_or_404(model_type[1], pk=pk)
        if learning_file.model.site not in self.request.user.userinfo.user_site_access():
            raise PermissionDenied()
        learning_file.delete_file()
        learning_file.delete()


class MembersCompleted(LoginRequiredMixin, AjaxMixin, View):
    data = {}
    models = {
        'theme': (models.Theme, models.ProfileTheme),
        'module': (models.Module, models.ProfileModule),
    }
    model_type = None

    def get(self, request, *args, **kwargs):
        """ Returns profile info for all profiles with completed model """
        model_type = self.models.get(self.kwargs.get('model_type'))
        pk = self.kwargs.get('pk')
        if not (model_type and pk):
            raise ValidationError('Insufficient Data')
        # Get members completed within site
        model = get_object_or_404(model_type[0], pk=pk)
        if model.site not in self.request.user.userinfo.user_site_access():
            raise PermissionDenied()
        members_completed = []
        for profile_model in model.profiles.all():
            if profile_model.date_completed:
                members_completed += [{
                    'name': str(profile_model.profile),
                    'pk': profile_model.profile.pk,
                    'date_completed': profile_model.date_completed.strftime('%m/%d/%Y'),
                }]
        self.data = {
            'profiles': json.dumps(members_completed)
        }
        return JsonResponse(self.data)

    def post(self, request, *args, **kwargs):
        """ Delete or add member to theme or modules members completed """
        if self.kwargs.get('delete'):
            # delete members training
            model, profile = self._get_args()
            profile_model = get_object_or_404(model.profiles, profile=profile)
            profile_model.delete()
        else:
            # add training to member
            model, profile = self._get_args()
            attrs = {self.kwargs.get('model_type'): model, 'profile': profile}
            profile_model = self.model_type[1](**attrs)
            profile_model.save()
        return JsonResponse(self.data)

    def _get_args(self):
        """ Get and validate arguments """
        self.model_type = self.models.get(self.kwargs.get('model_type'))
        pk = self.kwargs.get('pk')
        profile_pk = self.kwargs.get('profile_pk')
        if not (self.model_type and pk and profile_pk):
            raise ValidationError('Insufficient Data')
        model = get_object_or_404(self.model_type[0], pk=pk)
        profile = get_object_or_404(member_models.Profile, pk=profile_pk)
        if model.site not in self.request.user.userinfo.user_site_access():
            raise PermissionDenied()
        if profile not in self.request.user.userinfo.user_profile_access():
            raise PermissionDenied()
        return model, profile
