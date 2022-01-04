from django.shortcuts import render
import json
from datetime import datetime, date, time

from django.db.models import Value
from django.db import models as django_models
from django.db.models.functions import Concat
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView, View
from django.contrib.auth.models import User
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
                'users': list(User.objects.all().order_by('last_name').values_list('first_name', 'last_name')),
                'sites': self.request.user.userinfo.user_site_access_dict(),
                'extra_options': [{
                    'str': 'Adminstration',
                    'value': 'administration',
                    'options': [{'str': 'Application Administration', 'value': 'administration'}]
                }],
        }
        print(self.extra_context)
        return super(TemplateView, self).get_context_data(*args, **kwargs)


#     def get(self, request):
#         self.extra_context = {'user': self.request.user}
