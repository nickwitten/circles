from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from .models import DashboardContent
from itertools import zip_longest
import json


class MultiObjectView(TemplateView):
    """ View that handles rendering
        and saving forms for multiple
        related objects.  Make sure
        to set the objects to the
        desired values and implement
        get_instances
    """
    template_name = None
    success_url = None
    extra_context = dict()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.objects = {
                "object_name": {
                    "form_class": None,
                    "instance": None,
                    "initial_data": None,
                    "form_data": None,
                }
        }

    def get_instances(self, request, *args, **kwargs):
        """ You implement this.
            Objects and form_classes should
            be the same length, use None if
            no objects are found for that
            form_class.  You can use the
            request query string, or the
            args/kwargs passed to get()
        """
        return list()

    def get(self, request, *args, **kwargs):
        # pks = request.GET.get("pks", [])
        self.get_instances(request, *args, **kwargs)
        instances = [data["instance"] for data in self.objects.values()]
        return super().get(request, *args, forms=self.render_forms(), objects=instances, **kwargs)

    def post(self, request, *args, **kwargs):
        self.get_instances(request, *args, **kwargs)
        instances = [data["instance"] for data in self.objects.values()]
        for object_name, form_data in request.POST.dict().items():
            form_data = json.loads(form_data)
            self.objects[object_name]["form_data"] = form_data
        forms = self.render_forms()
        success = self.save_forms(forms)
        if success:
            return HttpResponseRedirect(self.get_success_url())
        return super().get(request, *args, forms=forms, objects=instances, **kwargs)

    def get_success_url(self):
        return self.success_url

    def render_forms(self):
        forms = [data["form_class"](prefix=name,
                            instance=data['instance'],
                            initial=data['initial_data'],
                            data=data['form_data']) \
                 for name, data in self.objects.items()]
        return forms

    def save_forms(self, forms):
        all_valid = all([form.is_valid() for form in forms])
        if all_valid:
            for form in forms:
                form.save()
        return all_valid



class DashboardListView(ListView):
    model = DashboardContent
    template_name = 'dashboard/dashboard.html'
    object_context_name = 'posts'
