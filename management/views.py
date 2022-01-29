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
from dashboard.views import MultiObjectView
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


class UserInfo(MultiObjectView):
    template_name = 'dashboard/ajax_form.html'
    extra_context = {
        'create_url_name': 'create-user',
        'update_url_name': 'update-user',
        'delete_url_name': 'delete-user',
        'object_name': 'User',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.objects = {
            "user": {
                "form_class": user_forms.UserRegisterForm,
                "instance": None,
                "initial_data": None,
                "form_data": None,
            },
            "userinfo": {
                "form_class": user_forms.UserInfoForm,
                "instance": None,
                "initial_data": None,
                "form_data": None,
            }
        }

    def get_instances(self, request, *args, **kwargs):
        pk = kwargs.pop("pk", None)
        user = User.objects.filter(pk=pk).first()
        self.objects["user"]["instance"] = user
        self.objects["userinfo"]["instance"] = user.userinfo if user is not None else None
        self.extra_context["object"] = user

    def save_forms(self, forms):
        all_valid = all([form.is_valid() for form in forms])
        if all_valid:
            user_form, userinfo_form = forms
            user = user_form.save()
            userinfo_form.save(user=user)
        return all_valid

    def get_success_url(self):
        return reverse("management")



class DeleteUserView(generic.DeleteView):
    model = User

    def get_success_url(self):
        return reverse("management")

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


class UpdateChapterView(generic.UpdateView):
    model = member_models.Chapter
    template_name = 'dashboard/ajax_form.html'
    form_class = member_forms.ChapterCreationForm
    extra_context = chapter_context

    def get_success_url(self):
        return reverse("management")


class DeleteChapterView(generic.DeleteView):
    model = member_models.Chapter

    def get_success_url(self):
        return reverse("management")


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

class UpdateSiteView(generic.UpdateView):
    model = member_models.Site
    template_name = 'dashboard/ajax_form.html'
    form_class = member_forms.SiteCreationForm
    extra_context = site_context

    def get_success_url(self):
        return reverse("management")


class DeleteSiteView(generic.DeleteView):
    model = member_models.Site

    def get_success_url(self):
        return reverse("management")


