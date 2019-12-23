from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import DashboardContent

# Create your views here.

class DashboardListView(ListView):
    model = DashboardContent
    template_name = 'dashboard/dashboard.html'
    object_context_name = 'posts'
