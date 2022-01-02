from django.shortcuts import render
import json
from datetime import datetime, date, time

from django.db.models import Value
from django.db import models as django_models
from django.db.models.functions import Concat
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView, View
# from django.contrib.auth.mixins import LoginRequiredMixin
# import members.models as member_models
# from members.data import unique_maintain_order
# from circles import settings
# from . import forms, models
# from django.core.exceptions import PermissionDenied, ValidationError


class Management(TemplateView):
    template_name = 'management/management.html'
