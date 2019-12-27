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
    filter_by = request.GET.get('filter_by',None) + '__icontains'
    filter_input = request.GET.get('filter_input',None)
    search_input = request.GET.get('search_input',None)
    sort_by = request.GET.get('sort_by',None)
    data_displayed = request.GET.get('data_displayed',None)
    data_displayed = json.loads(data_displayed)
    saved_filters = request.GET.get('saved_filters',None)
    saved_filters = json.loads(saved_filters)
    profiles = Profile.objects.all()
    sorted_profiles = []

    ######## filter feature (filter without yet adding to saved filters) ######

    if filter_by == '__icontains': # No filter active
        profiles = profiles
    else:
        # Only filter out if there is an input
        if filter_input != '' or filter_input != None:
            filter = {}
            filter[filter_by] = filter_input
            # Only profiles that pass the filter
            profiles = profiles.filter(**filter)

    # Saved filters (filters that have been added)
    # List of [(filterby, filterinput)]
    for filter in saved_filters:
        # Only filter out if there is an input
        if filter["filterinput"] != '' or filter["filterinput"] != None:
            query = {}
            query[filter["filterby"] + '__icontains'] = filter["filterinput"]
            profiles = profiles.filter(**query)

    ################### search feature #########################

    search = {}
    # Anotate each profile with 'firstname lastname'
    annotated_queryset = profiles.annotate(fullname = Concat('first_name', Value(' '), 'last_name'))
    # Filter out elements that don't contain search input
    profiles = annotated_queryset.filter(fullname__icontains=search_input)


    ################## sort and data feature ##################

    # Types of data that need to be fetched from a residence model
    residence_data = ['street_address','city','state','zip']

    # Loop through every profile
    for profile in profiles:
        # Get requested data for profile
        data = []
        for data_type in data_displayed: # Loop through requested data
            data_temp = None
            if data_type: # if data is requested
                # If data requested is part of the residence model
                if (data_type in residence_data):
                    # Get the current residence model
                    residence = profile.order_residences().first()
                    # If one was found get the data
                    if residence:
                        data_temp = getattr(residence,data_type)
                # If data requested is part of children model
                elif (data_type == 'children'):
                    children = profile.order_children() # Get children
                    data_temp = ''
                    for child in children:
                        data_temp += child.first_name + ' '
                else:
                    data_temp = getattr(profile,data_type) # fetch data
                 # If data is a phone number
                if data_temp and ((data_type == 'cell') or (data_type == 'e_phone')):
                    data_temp = data_temp.as_e164 # Turn into a string
                if not data_temp: # if the field is empty return not available
                    data_temp = 'not available'
                data.append(data_temp) # Add that data result to list of data
        if sort_by == '':
            group_name = 'no groups' # User doesn't want them sorted
        elif (sort_by in residence_data): # If sort data is in residence model
            # Get the current residence model
            residence = profile.order_residences().first()
            # If one was found get the data
            if residence:
                group_name = getattr(residence,sort_by)
            else:
                group_name = None
        else:
            group_name = getattr(profile,sort_by) # Get the requested sort attribute
        if group_name == None:
            # Profile has no data for this field
            group_name = 'Not Assigned'
        # Loop through list of groups (a group is a dictionary)
        profile_added = False
        for group in sorted_profiles:
            if group_name == group['group name']: # Same group
                group['profiles'].append(
                    {
                        'first name' : profile.first_name,
                        'last name' : profile.last_name,
                        'pk' : profile.pk,
                        'data' : data
                    }
                ) # Add the profile to this group
                profile_added = True
                break
        if not profile_added: # No other group member in list yet.  Make
            # new group
            sorted_profiles.append(
                {
                    'group name': group_name,
                    'profiles': [
                        {
                            'first name' : profile.first_name,
                            'last name' : profile.last_name,
                            'pk' : profile.pk,
                            'data' : data
                        }
                    ]
                }
            )

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
