from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import DashboardContent


class MultiObjectView(TemplateView):
    form_classes = list()
    objects = list()
    initial = dict()
    extra_context = dict()

    def get_objects(self, request, *args, **kwargs):
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
        self.objects = self.get_objects(request, *args, **kwargs)
        return super().get(request, *args, forms=self.render_forms(), objects=self.objects, **kwargs)

    def post(self, request):
        pass

    def render_forms(self):
        assert len(self.form_classes) == len(self.objects)
        if self.request.method == "POST":
            forms = [form_class(instance=instance, initial=self.initial) \
                    for form_class, instance in zip(self.form_classes, self.objects)]
        if self.request.method == "GET":
            forms = [form_class(instance=instance, initial=self.initial) \
                    for form_class, instance in zip(self.form_classes, self.objects)]
        return forms



class DashboardListView(ListView):
    model = DashboardContent
    template_name = 'dashboard/dashboard.html'
    object_context_name = 'posts'
