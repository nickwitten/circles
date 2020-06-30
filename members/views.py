from django.shortcuts import render, redirect
from django.views.generic import ListView,CreateView,DetailView,UpdateView,DeleteView,TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from .models import Profile, Residence, Role, Training, Child, ChildInfo, FilterSet
from . import forms
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.db.models.functions import Concat
from django.db.models import Value
from django.http import JsonResponse, HttpResponse
from django.core import serializers
import json
from .data import get_profiles, get_field_options, create_excel, form_choices_text



# Create your views here.

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    # template_name = 'members/profile_detail.html'
    template_name = 'members/profile_detail.html'

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    # template_name = 'members/create_profile.html'
    template_name = 'members/update_profile.html'
    form_class = forms.ProfileUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProfileDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Profile
    template_name = 'members/modal_delete.html'
    success_message = 'Deleted'

    def get_success_url(self):
        return reverse('profiles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'profile'
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        context['instance'] = profile.first_name + ' ' + profile.last_name
        return context

def create_profile(request):
    if request.method == 'POST':
        form = forms.ProfileCreationForm(request.POST)
        if form.is_valid():
            site = form.cleaned_data['site']
            position = form.cleaned_data['position']
            new_profile = form.save()
            role = Role(site=site, position=position, profile=new_profile)
            role.save()
            return redirect('profile-update',new_profile.pk)
    else:
        form = forms.ProfileCreationForm(user=request.user)

    context = {
        'form': form,
        'object': Profile,
    }
    # return render(request, 'members/create_profile.html',context)
    return render(request, 'members/create_profile.html',context)


class ResidenceCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Residence
    template_name = 'members/modal_create.html'
    form_class = forms.ResidenceCreationForm

    def form_valid(self,form):
        residence = form.save(commit=False)
        residence.profile = Profile.objects.get(pk=self.kwargs['pk'])
        return super(ResidenceCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('profile-update', args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Home Information'
        return context

class ResidenceUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Residence
    template_name = 'members/modal_create.html'
    form_class = forms.ResidenceCreationForm

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Home Information'
        return context

class ResidenceDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Residence
    template_name = 'members/modal_delete.html'
    success_message = 'Deleted'

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'home information'
        context['instance'] = Residence.objects.get(pk=self.kwargs['pk']).street_address
        return context


class RoleCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Role
    template_name = 'members/modal_create.html'
    form_class = forms.RoleCreationForm

    def form_valid(self,form):
        role = form.save(commit=False)
        role.profile = Profile.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile-update', args=(self.object.profile.id,))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Role'
        return context


class RoleUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Role
    template_name = 'members/modal_create.html'
    form_class = forms.RoleCreationForm

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Role'
        return context

class RoleDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Role
    template_name = 'members/modal_delete.html'
    success_message = 'Deleted'

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'role'
        context['instance'] = Role.objects.get(pk=self.kwargs['pk']).position
        return context


class TrainingAddView(LoginRequiredMixin, BSModalCreateView):
    model = Training
    template_name = 'members/modal_create.html'
    form_class = forms.TrainingAddForm

    def form_valid(self,form):
        role = form.save(commit=False)
        role.profile = Profile.objects.get(pk=self.kwargs['pk'])
        return super(TrainingAddView, self).form_valid(form)

    def get_success_url(self):
        return reverse('profile-update', args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Training'
        return context

class TrainingUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Training
    template_name = 'members/modal_create.html'
    form_class = forms.TrainingAddForm

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Training'
        return context

class TrainingDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Training
    template_name = 'members/modal_delete.html'
    success_message = 'Deleted'

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'training'
        context['instance'] = Training.objects.get(pk=self.kwargs['pk']).subject
        return context

def ChildrenEditView(request,pk):
    profile = Profile.objects.get(pk=pk)
    childinfos = profile.get_child_infos()
    context = {
        'profile_pk' : pk,
        'profile' : profile,
        'childinfos' : childinfos,
    }
    return render(request,'members/children_edit.html',context)

class ChildInfoCreateView(LoginRequiredMixin, BSModalCreateView):
    model = ChildInfo
    template_name = 'members/modal_create.html'
    form_class = forms.ChildInfoCreationForm

    def form_valid(self,form):
        childinfo = form.save(commit=False)
        childinfo.profile = Profile.objects.get(pk=self.kwargs['pk'])
        return super(ChildInfoCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('edit-children', args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Set'
        return context

class ChildInfoUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = ChildInfo
    template_name = 'members/modal_create.html'
    form_class = forms.ChildInfoCreationForm

    def get_success_url(self):
        return reverse('edit-children',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Information'
        return context

class ChildInfoDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = ChildInfo
    template_name = 'members/modal_delete.html'
    success_message = 'Deleted'

    def get_success_url(self):
        return reverse('edit-children',args=(self.object.profile.id,))

class ChildCreateView(LoginRequiredMixin, CreateView):
    model = Child
    template_name = 'members/modal_create.html'
    form_class = forms.ChildCreationForm

    def form_valid(self,form):
        child = form.save(commit=False)
        child.child_info = ChildInfo.objects.get(pk=self.kwargs['pk'])
        return super(ChildCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('edit-children', args=(self.object.child_info.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Child'
        return context

class ChildUpdateView(LoginRequiredMixin, UpdateView):
    model = Child
    template_name = 'members/modal_create.html'
    form_class = forms.ChildCreationForm

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.child_info.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Child Info'
        return context

class ChildDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Child
    template_name = 'members/modal_delete.html'
    success_message = 'Deleted'

    def get_success_url(self):
        return reverse('edit-children',args=(self.object.child_info.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'child'
        context['instance'] = Child.objects.get(pk=self.kwargs['pk']).first_name
        return context

def profiles(request):
    filterset_objects = request.user.filtersets.all()
    form = forms.ProfilesToolsForm
    context = {
        'form': form,
        'form_choices_text': form_choices_text,
        'form_choices_text_json': json.dumps(form_choices_text),
        'filterset_objects' : filterset_objects,
    }

    return render(request, 'members/profiles.html',context)

# Get profiles view that returns profile data
def GetProfiles(request):
    tools_form = forms.ProfilesToolsForm(request.GET)
    if tools_form.is_valid():
        tool_inputs = tools_form.cleaned_data
        data = get_profiles(tools_form.cleaned_data, request.user)
        return JsonResponse(data)
    print()
    print('FORM INVALID')
    print()

def UserFiltersets(request):
    filterset_object = None
    if request.POST:
        title = request.POST.get('title', None)
        filters = request.POST.get('filters',None)
        pk = request.POST.get('pk', None)
        delete = request.POST.get('delete', None)
        if pk:
            filterset_object = FilterSet.objects.get(pk=pk)
            if delete:
                filterset_object.delete()
            # Update title
            else:
                filterset_object.title = title
                filterset_object.save()
        # Create new filterset if pk not provided
        else:
            filterset_object = FilterSet(user=request.user,filterset=filters)
            filterset_object.save()
    # Get the objects associated to the current user
    filterset_objects = request.user.filtersets.all()
    filtersets = []
    for filterset in filterset_objects:
        filtersets.append({
            "title": filterset.title,
            "filters": filterset.filterset,
            "pk": filterset.pk,
        })
    data = {
        'filtersets': filtersets,
        'pk': filterset_object.pk if filterset_object else None
    }
    return JsonResponse(data)

# Gets a fields options
def FilterInput(request):
    filterby = request.GET.get('filterby',None)
    if filterby:
        options = get_field_options(filterby)
    else:
        options = []
    data = {
        'options':options,
    }
    return JsonResponse(data)

# Creates an excel document
def ExcelDump(request):
    tools_form = forms.ProfilesToolsForm(request.POST)
    if tools_form.is_valid():
        tool_inputs = tools_form.cleaned_data
        print(tool_inputs)
        sorted_profiles = get_profiles(tool_inputs, request.user)
        output = create_excel(tool_inputs, sorted_profiles)
        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        return response
    else:
        print()
        print('INVALID FORM')
        print()
