from django.shortcuts import render, redirect
from django.views.generic import ListView,CreateView,DetailView,UpdateView,DeleteView,TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from .models import Profile, Residence, Role, Training, Child, ChildInfo, FilterSet
from .forms import ProfileCreationForm, ResidenceCreationForm, RoleCreationForm, TrainingAddForm, ChildCreationForm, ChildInfoCreationForm
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.db.models.functions import Concat
from django.db.models import Value
from django.http import JsonResponse
from django.core import serializers
import json
from .data import search_profiles, filter_profiles, get_profile_data, sort_profiles


# Create your views here.

class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    context_object_name = 'profiles'
    template_name = 'members/profiles.html'

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'members/profile_detail.html'

class ProfileCreateView(LoginRequiredMixin, CreateView):
    model = Profile
    template_name = 'members/create_profile.html'
    form_class = ProfileCreationForm
    def form_valid(self,form):
        self.object = form.save()
        return redirect('profile-update',self.object.id)

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'members/create_profile.html'
    form_class = ProfileCreationForm

class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = Profile
    success_url = '/members'

def create_profile(request):
    if request.method == 'POST':
        p_form = ProfileCreationForm(request.POST)
        r_form = ResidenceCreationForm(request.POST)
        if p_form.is_valid() and r_form.is_valid():
            new_profile = p_form.save()
            r_form.save()
            return redirect('profile-detail',new_profile.pk)
    else:
        p_form = ProfileCreationForm()
        r_form = ResidenceCreationForm()

    context = {
        'p_form' : p_form,
        'r_form' : r_form,
    }
    return render(request, 'members/create_profile.html',context)

def update_profile(request,pk):
    object = Profile.objects.get(pk=pk)
    residences = object.order_residences()
    if request.method == 'POST':
        p_form = ProfileCreationForm(request.POST, instance=object)
        r_form = ResidenceCreationForm(request.POST, instance=residences.first())
        if p_form.is_valid() and r_form.is_valid():
            p_form.save()
            r_form.save()
            return redirect('profile-detail',pk)
    else:
        p_form = ProfileCreationForm(instance = object)
        r_form = ResidenceCreationForm(instance = object.residences.first())

    context = {
        'p_form' : p_form,
        'r_form' : r_form,
        'object' : object
    }
    return render(request, 'members/create_profile.html',context)

class ResidenceCreateView(LoginRequiredMixin, BSModalCreateView):
    model = Residence
    template_name = 'members/modal_create.html'
    form_class = ResidenceCreationForm

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
    form_class = ResidenceCreationForm

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
    form_class = RoleCreationForm

    def form_valid(self,form):
        role = form.save(commit=False)
        role.profile = Profile.objects.get(pk=self.kwargs['pk'])
        return super(RoleCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('profile-update', args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Role'
        return context

class RoleUpdateView(LoginRequiredMixin, BSModalUpdateView):
    model = Role
    template_name = 'members/modal_create.html'
    form_class = RoleCreationForm

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
    form_class = TrainingAddForm

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
    form_class = TrainingAddForm

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
    form_class = ChildInfoCreationForm

    def form_valid(self,form):
        childinfo = form.save(commit=False)
        childinfo.profile = Profile.objects.get(pk=self.kwargs['pk'])
        return super(ChildInfoCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('edit-children', args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = ''
        return context

class ChildCreateView(LoginRequiredMixin, CreateView):
    model = Child
    template_name = 'members/modal_create.html'
    form_class = ChildCreationForm

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
    form_class = ChildCreationForm

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.child_info.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Child Info'
        return context

def profiles(request):
    filterset_objects = request.user.filtersets.all()
    context = {
        'filterset_objects' : filterset_objects
    }

    return render(request, 'members/profiles.html',context)

# Returns a list of html link elements of profiles that match the active filters,
# search input, and are sorted.
def GetProfiles(request):
    # Receive data
    search_input = request.GET.get('search_input',None)
    sort_by = request.GET.get('sort_by',None)
    data_displayed = request.GET.get('data_displayed',None)
    data_displayed = json.loads(data_displayed)
    filters = request.GET.get('filters',None)
    filters = json.loads(filters)
    profiles = Profile.objects.all()

    profiles = search_profiles(profiles,search_input)
    profiles = filter_profiles(profiles,filters)
    profiles = get_profile_data(profiles,data_displayed)
    sorted_profiles = sort_profiles(profiles,sort_by)

    data = {
        'groups' : sorted_profiles
    }

    return JsonResponse(data)

# Add a filterset to the current user
def CreateFilterset(request):
    # Obtain the current filters
    filters = request.GET.get('filters',None)
    # Create a FilterSet model to be saved to the user
    filterset = FilterSet(user=request.user,filterset=filters)
    filterset.save() # Save the model
    data = {
    }

    return JsonResponse(data)

# Returns the filtersets of the user
def GetFiltersets(request):
    # Get the objects associated to the current user
    filterset_objects = request.user.filtersets.all()
    # Create a dictionary for the filtersets to be in
    data = {
        'filtersets' : []
    }
    # Add each filterset to the dictionary as its own dictionary
    for filterset in filterset_objects:
        data["filtersets"].append(
            {
                "title": filterset.title,
                "filters": filterset.filterset
            }
        )

    return JsonResponse(data)

# Adds a title to the created filterset
def AddFiltersetTitle(request):
    # receive data
    title = request.GET.get('title',None)
    filters = request.GET.get('filters',None)
    # Get the active filterset
    filterset_object = request.user.filtersets.filter(filterset=filters).first()
    # Assign a title
    filterset_object.title = title
    filterset_object.save()
    data = {
        'object_title' : filterset_object.title,
    }

    return JsonResponse(data)

# Deletes a user's filterset
def DeleteFilterset(request):
    # Receive data
    user = request.user
    filters = request.GET.get('filters',None)
    title = request.GET.get('title',None)
    # Delete the active filterset
    request.user.filtersets.filter(title=title, filterset=filters).first().delete()
    data = {
    }
    return JsonResponse(data)
