from django.db.models import Value
from django.db.models.functions import Concat
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView, View, ContextMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
import members.models as member_models
from . import forms, models


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
    models = {
        'programming': models.Programming,
        'theme': models.Theme,
        'module': models.Module,
    }

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('pk'):
            self.get_model_info()
        elif self.kwargs.get('editing_models'):
            self.check_existing()
        elif self.kwargs.get('autocomplete_search'):
            self.autocomplete()
        elif self.kwargs.get('autocomplete_facilitator_search'):
            self.autocomplete_facilitator()
        else:
            raise Http404('No Matching Kwargs')
        return JsonResponse(self.data)

    def post(self, request, *args, **kwargs):
        for model in self.kwargs.get('models'):
            if model.get('pk'):
                # Check if access and update model (don't
                # change facilitators, change files)
                pass
            else:
                # Check if access and create model
                pass

    def get_model_info(self):
        """ Gets dictionary of model information if the user has access. """
        pk = self.kwargs['pk']
        cls = self.models.get(self.kwargs.get('model_type'))
        model = None
        if cls:
            model = get_object_or_404(cls, pk=pk)
        if not model or model.site not in self.request.user.userinfo.user_site_access():
            raise Http404()
        self.data = model.to_dict()

    def check_existing(self):
        pass

    def autocomplete(self):
        """" Gets names of similar models even without site access """
        search = self.kwargs['autocomplete_search']
        cls = self.models.get(self.kwargs.get('model_type'))
        if not (search and cls):
            raise Http404()
        results = cls.objects.filter(title__icontains=search).values_list('title')
        results = [match[0] for match in results]
        # Sort by frequency
        results = sorted(results, key=results.count, reverse=True)
        # Get distinct while maintaining order
        seen = set()
        seen_add = seen.add
        results = [x for x in results if not (x in seen or seen_add(x))]
        self.data = {'results': results}

    def autocomplete_facilitator(self):
        search = self.kwargs['autocomplete_facilitator_search']
        site = get_object_or_404(member_models.Site, pk=self.kwargs.get('site_pk'))
        if site not in self.request.user.userinfo.user_site_access():
            raise Http404()
        results = member_models.Profile.objects.filter(roles__site=site)
        results = results.annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
        results = results.filter(fullname__icontains=search).values_list('first_name', 'last_name', 'pk')
        results = set(results)
        results = [[match[0] + ' ' + match[1], match[2]] for match in results]
        self.data = {'results': results}


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
