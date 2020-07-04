from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView, View, ContextMixin
from django.contrib.auth.mixins import LoginRequiredMixin
import members.models as member_models
from . import forms


class AjaxMixin(ContextMixin):

    def setup(self, request, *args, **kwargs):
        kwargs.update(dict(getattr(request, 'GET', None) or getattr(request, 'POST', None)))
        super().setup(request, *args, **kwargs)

    def response(self, **kwargs):
        data = self.get_context_data(**kwargs)
        return JsonResponse(data)


class Learning(LoginRequiredMixin, TemplateView):

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

    def get(self, request, *args, **kwargs):
        context = {}
        if self.kwargs.get('pk'):
            self.get_model_info()
        elif self.kwargs.get('autocomplete_model'):
            self.autocomplete()
        elif self.kwargs.get('autocomplete_facilitator'):
            self.autocomplete()
        elif self.kwargs.get('models'):
            self.check_existing()
        else:
            raise Http404('No Matching Kwargs')
        self.response(**context)

    def post(self, request, *args, **kwargs):
        context = {}
        for model in self.kwargs.get('models'):
            if model.get('pk'):
                # Check if access and update model (don't
                # change facilitators, change files)
                pass
            else:
                # Check if access and create model
                pass
        self.response(**context)

    def get_model_info(self):
        pass

    def check_existing(self):
        pass

    def autocomplete(self):
        pass


class LearningFiles(LoginRequiredMixin, AjaxMixin, View):

    def post(self):
        context = {}
        if self.kwargs.get('pk'):
            # delete file
            pass
        else:
            # create file
            pass
        self.response(**context)

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
        self.response(**context)

    def post(self, request, *args, **kwargs):
        context = {}
        if self.kwargs.get('delete'):
            # delete members training
            pass
        else:
            # add training to member
            pass
        self.response(**context)