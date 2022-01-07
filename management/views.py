from django.shortcuts import render
import json
from datetime import datetime, date, time

from django.db.models import Value
from django.db import models as django_models
from django.db.models.functions import Concat
from django.http import JsonResponse, QueryDict
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView, View
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from django.views import generic
from users import forms as user_forms
from users import models as user_models
from members import forms as member_forms
from members import models as member_models
# from django.contrib.auth.mixins import LoginRequiredMixin
# import members.models as member_models
# from members.data import unique_maintain_order
# from circles import settings
# from . import forms, models
# from django.core.exceptions import PermissionDenied, ValidationError


class Management(TemplateView):
    template_name = 'management/management.html'

    def get_context_data(self, *args, **kwargs):
        self.extra_context = {
                'user': self.request.user,
                'users': User.objects.all(),
                'sites': self.request.user.userinfo.user_site_access_dict(),
                'extra_options': [{
                    'str': 'Adminstration',
                    'value': 'administration',
                    'options': [{'str': 'Application Administration', 'value': 'administration'}]
                }],
        }
        return super(Management, self).get_context_data(*args, **kwargs)


#     def get(self, request):
#         self.extra_context = {'user': self.request.user}

class UserInfo(TemplateView):
    template_name = 'dashboard/ajax_form.html'
    model_classes = [User, user_models.UserInfo]
    form_classes = [user_forms.UserRegisterForm, user_forms.UserInfoForm]
    objects = [None, None]
    initial = {}
    extra_context = {
        'create_url_name': 'create-user',
        'update_url_name': 'update-user',
        'delete_url_name': 'delete-user',
        'object_name': 'User',
    }

    def render_forms(self):
        if self.request.method == "POST":
            forms = [form_class(instance=instance, initial=self.initial) \
                    for form_class, instance in zip(self.form_classes, self.objects)]
        if self.request.method == "GET":
            forms = [form_class(instance=instance, initial=self.initial) \
                    for form_class, instance in zip(self.form_classes, self.objects)]
        return forms

    def get(self, request, *args, **kwargs):
        pk = kwargs.pop("pk", None)
        user = User.objects.filter(pk=pk).first()
        userinfo = user.userinfo if user is not None else None
        self.objects = [user, userinfo]
        return super(UserInfo, self).get(request, *args, forms=self.render_forms(), object=user, **kwargs)

    def post(self, request):
        pass

chapter_context = {
    'create_url_name': 'create-chapter',
    'update_url_name': 'update-chapter',
    'delete_url_name': 'delete-chapter',
    'object_name': 'Chapter',
}
class CreateChapterView(generic.CreateView):
    model = member_models.Chapter
    template_name = 'dashboard/ajax_form.html'
    form_class = member_forms.ChapterCreationForm
    extra_context = chapter_context

    def get_success_url(self):
        return reverse("management")

class UpdateChapterView(generic.CreateView):
    model = member_models.Chapter
    template_name = 'dashboard/ajax_form.html'
    form_class = member_forms.ChapterCreationForm
    extra_context = chapter_context

class DeleteChapterView(generic.CreateView):
    model = member_models.Chapter

site_context = {
    'create_url_name': 'create-site',
    'update_url_name': 'update-site',
    'delete_url_name': 'delete-site',
    'object_name': 'Site',
}
class CreateSiteView(generic.CreateView):
    model = member_models.Site
    template_name = 'dashboard/ajax_form.html'
    form_class = member_forms.SiteCreationForm
    extra_context = site_context

    def get_success_url(self):
        return reverse("management")

class UpdateSiteView(generic.CreateView):
    model = member_models.Site
    template_name = 'dashboard/ajax_form.html'
    form_class = member_forms.SiteCreationForm
    extra_context = site_context

class DeleteSiteView(generic.CreateView):
    model = member_models.Site

