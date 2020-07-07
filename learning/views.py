import json
from django.db.models import Value
from django.db.models.functions import Concat
from django.http import Http404, HttpResponseServerError, JsonResponse, QueryDict
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView, View, ContextMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
import members.models as member_models
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
        context['role_types'] = member_models.Role.position_choices
        context['programming_form'] = forms.ProgrammingCreationForm()
        context['theme_form'] = forms.ThemeCreationForm()
        context['module_form'] = forms.ModuleCreationForm()
        context['chapter_info'] = self.chapter_info()
        return context

    def chapter_info(self):
        chapters = self.request.user.userinfo.user_site_access_dict()
        chapter_info = []
        for chapter in chapters:
            temp_chapter = {'chapter': chapter['chapter'], 'sites': []}
            sites = chapter['sites']
            for site in sites:
                temp_chapter['sites'] += [{
                    'site': site,
                    'programming': site.programming.all(),
                    'themes': [{'theme': theme, 'modules': theme.modules.all()} for theme in site.themes.all()]
                }]
            chapter_info += [temp_chapter]
        return chapter_info


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
            raise ValidationError('No Matching Kwargs', code=500)
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
        pass

    def create_or_update_models(self):
        """ Takes {site, (theme), title, (pk)} objects for each
            model that needs to be updated or created.  Theme
            required if model is module.  Pk required if model
            already exists.                                     """
        model_type, form_data, model_infos = self._get_args()
        for info in model_infos:
            attrs, pk, replace_pk = self._get_model_info(model_type, info)
            if pk:
                self._update_model(model_type, attrs, pk,
                                   replace_pk, form_data)
            else:
                self._create_model(model_type, attrs, form_data)

    def _get_args(self):
        """ Process create_or_update_models args """
        model_type = self.models.get(self.kwargs.get('model_type'))
        form_data = self.kwargs.get('form')
        form_fields = self.kwargs.get('fields')
        model_infos = self.kwargs.get('models')
        if not (model_type and form_data and form_fields and model_infos):
            raise ValidationError('Insufficient Data', code=500)
        form_data = QueryDict(form_data)
        # Only edit specified fields
        if form_fields != 'all':
            for field in form_data.keys():
                if field not in form_fields:
                    form_data.pop(field)
        model_infos = json.loads(model_infos)
        return model_type, form_data, model_infos

    def _get_model_info(self, model_type, info):
        """ Unpack and validate model info """
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
            theme = models.Theme.objects.filter(title=theme, **attrs).first()
            # Theme doesn't exist in this site so create
            if not theme:
                theme.objects.create(title=theme, **attrs)
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
            # Check for models with same info
            replace = model_type[0].objects.filter(
                title=form.cleaned_data['title'], **attrs
            ).exclude(pk=pk).first()
            if replace:
                # Validate user meant to replace
                if replace_pk != replace.pk:
                    raise ValidationError('Unexpected Replacement')
                model = form.save(**attrs)
                for profile in replace.profiles.all():
                    model.profiles.add(profile)
                for profile in replace.facilitator_profiles.all():
                    model.facilitator_profiles.add(profile)
                replace.delete()
            else:
                model = form.save(**attrs)

    @staticmethod
    def _create_model(model_type, attrs, form_data):
        form = model_type[2](form_data)
        if form.is_valid():
            # Verify that no model with this info exists
            if model_type[0].objects.filter(title=form.cleaned_data['title'], **attrs):
                raise ValidationError('Model Already Exists ID Required', code=500)
            model = form.save(**attrs)


class LearningFiles(LoginRequiredMixin, AjaxMixin, View):

    def post(self):
        context = {}
        if self.kwargs.get('pk'):
            # delete file
            pass
        else:
            # create file
            pass

class MembersCompleted(LoginRequiredMixin, AjaxMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        site = self.kwargs.get('type')
        model_type = self.kwargs.get('model_type')
        model_pk = self.kwargs.get('model_pk')
        if site and model_type and model_pk:
            # Get members completed within site
            pass
        else:
            raise Http404()

    def post(self, request, *args, **kwargs):
        context = {}
        if self.kwargs.get('delete'):
            # delete members training
            pass
        else:
            # add training to member
            pass
