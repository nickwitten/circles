from django.shortcuts import render, redirect
from django.views.generic import CreateView,DetailView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import QueryDict, Http404
from .models import Profile, Residence, Role, Training, Child, ChildInfo, FilterSet
from . import forms
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.http import JsonResponse, HttpResponse
import json
from .data import get_profiles, get_field_options, create_excel, form_choices_text



# Create your views here.

class SiteAccessMixin:

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        accessible_sites = self.request.user.userinfo.user_site_access()
        if self.model == Profile:
            if obj.roles.filter(site__in=accessible_sites):
                return obj
        else:
            if obj.profile.roles.filter(site__in=accessible_sites):
                return obj
        raise Http404('Access Denied')

    def form_valid(self,form):
        if self.model == Profile:
            if self.object:
                # profile is being created
                if not self.object.roles.filter(site__in=self.request.user.userinfo.user_site_access()):
                    raise Http404('Profile Access Denied')
            return super().form_valid(form)
        else:
            new_instance = form.save(commit=False)
            if not self.object:
                # Object is being created
                profile = Profile.objects.get(pk=self.kwargs['pk'])
                if profile.roles.filter(site__in=self.request.user.userinfo.user_site_access()):
                    new_instance.profile = profile
                else:
                    raise Http404('Profile Access Denied')
            else:
                # Object is being updated
                profile = self.object.profile
                if not profile.roles.filter(site__in=self.request.user.userinfo.user_site_access()):
                    raise Http404('Access Denied')
            return super().form_valid(form)


class ProfileDetailView(LoginRequiredMixin, SiteAccessMixin, DetailView):
    model = Profile
    template_name = 'members/profile_detail.html'


class ProfileUpdateView(LoginRequiredMixin, SiteAccessMixin, UpdateView):
    model = Profile
    template_name = 'members/update_profile.html'
    form_class = forms.ProfileUpdateForm


class ProfileDeleteView(LoginRequiredMixin, SiteAccessMixin, BSModalDeleteView):
    model = Profile
    template_name = 'members/modal_delete.html'
    success_message = 'Deleted'

    def get_success_url(self):
        return reverse('profiles')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'profile'
        profile = self.object
        context['instance'] = profile.first_name + ' ' + profile.last_name
        return context


def create_profile(request):
    if not request.user.is_authenticated:
        raise Http404()
    if request.method == 'POST':
        form = forms.ProfileCreationForm(request.POST, user=request.user)
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
    return render(request, 'members/create_profile.html',context)


class ResidenceCreateView(LoginRequiredMixin, SiteAccessMixin, BSModalCreateView):
    model = Residence
    template_name = 'members/modal_create.html'
    form_class = forms.ResidenceCreationForm

    def get_success_url(self):
        return reverse('profile-update', args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Home Information'
        return context

class ResidenceUpdateView(LoginRequiredMixin, SiteAccessMixin, BSModalUpdateView):
    model = Residence
    template_name = 'members/modal_create.html'
    form_class = forms.ResidenceCreationForm

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Home Information'
        return context

class ResidenceDeleteView(LoginRequiredMixin, SiteAccessMixin, BSModalDeleteView):
    model = Residence
    template_name = 'members/modal_delete.html'
    success_message = 'Deleted'

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'home information'
        context['instance'] = self.object.street_address
        return context


class RoleCreateView(LoginRequiredMixin, SiteAccessMixin, BSModalCreateView):
    model = Role
    template_name = 'members/modal_create.html'
    form_class = forms.RoleCreationForm

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


class RoleUpdateView(LoginRequiredMixin, SiteAccessMixin, BSModalUpdateView):
    model = Role
    template_name = 'members/modal_create.html'
    form_class = forms.RoleCreationForm

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Role'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class RoleDeleteView(LoginRequiredMixin, SiteAccessMixin, BSModalDeleteView):
    model = Role
    template_name = 'members/modal_delete.html'
    success_message = 'Deleted'

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'role'
        context['instance'] = self.object.position
        return context


class TrainingAddView(LoginRequiredMixin, SiteAccessMixin, BSModalCreateView):
    model = Training
    template_name = 'members/modal_create.html'
    form_class = forms.TrainingAddForm

    def get_success_url(self):
        return reverse('profile-update', args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Training'
        return context

class TrainingUpdateView(LoginRequiredMixin, SiteAccessMixin, BSModalUpdateView):
    model = Training
    template_name = 'members/modal_create.html'
    form_class = forms.TrainingAddForm

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Training'
        return context

class TrainingDeleteView(LoginRequiredMixin, SiteAccessMixin, BSModalDeleteView):
    model = Training
    template_name = 'members/modal_delete.html'
    success_message = 'Deleted'

    def get_success_url(self):
        return reverse('profile-update',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'training'
        context['instance'] = self.object.subject
        return context


class ChildrenEditView(LoginRequiredMixin, SiteAccessMixin, DetailView):
    model = Profile
    template_name = 'members/children_edit.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        childinfos = self.object.get_child_infos()
        context = {
            'childinfos': childinfos,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ChildInfoCreateView(LoginRequiredMixin, SiteAccessMixin, BSModalCreateView):
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

class ChildInfoUpdateView(LoginRequiredMixin, SiteAccessMixin, BSModalUpdateView):
    model = ChildInfo
    template_name = 'members/modal_create.html'
    form_class = forms.ChildInfoCreationForm

    def get_success_url(self):
        return reverse('edit-children',args=(self.object.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Information'
        return context

class ChildInfoDeleteView(LoginRequiredMixin, SiteAccessMixin, BSModalDeleteView):
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
        if not child.child_info.profile.roles.filter(site__in=self.request.user.userinfo.user_site_access()):
            raise Http404('Access Denied')
        return super().form_valid(form)

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

    def form_valid(self,form):
        if not self.object.child_info.profile.roles.filter(site__in=self.request.user.userinfo.user_site_access()):
            raise Http404('Access Denied')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('edit-children',args=(self.object.child_info.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Child Info'
        return context

class ChildDeleteView(LoginRequiredMixin, BSModalDeleteView):
    model = Child
    template_name = 'members/modal_delete.html'
    success_message = 'Deleted'

    def get_object(self, *args, **kwargs):
        child = super().get_object(*args, **kwargs)
        accessible_sites = self.request.user.userinfo.user_site_access()
        if child.child_info.profile.roles.filter(site__in=accessible_sites):
            return child
        raise Http404('Access Denied')

    def get_success_url(self):
        return reverse('edit-children',args=(self.object.child_info.profile.id,))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'child'
        context['instance'] = self.object.first_name
        return context

def profiles(request):
    if not request.user.is_authenticated:
        raise Http404()
    filterset_objects = request.user.filtersets.all()
    form = forms.ProfilesToolsForm
    list_form = forms.UserListForm
    context = {
        'form': form,
        'list_form': list_form,
        'form_choices_text': form_choices_text,
        'form_choices_text_json': json.dumps(form_choices_text),
        'filterset_objects' : filterset_objects,
    }

    return render(request, 'members/profiles.html',context)

# Get profiles view that returns profile data
def GetProfiles(request):
    if not request.user.is_authenticated:
        raise Http404()
    tools_form = forms.ProfilesToolsForm(request.GET)
    if tools_form.is_valid():
        tool_inputs = tools_form.cleaned_data
        data = get_profiles(tools_form.cleaned_data, request.user)
        return JsonResponse(data)
    print()
    print('FORM INVALID')
    print()

def UserFiltersets(request):
    if not request.user.is_authenticated:
        raise Http404()
    filterset_object = None
    if request.POST:
        form_ser = request.POST.get('form', None)
        form_dict = QueryDict(form_ser)
        pk = request.POST.get('pk', None)
        delete = request.POST.get('delete', None)
        if pk:
            filterset_object = FilterSet.objects.get(pk=pk)
            if delete:
                filterset_object.delete()
            # Update title
            else:
                form = forms.UserListForm(form_dict, instance=filterset_object)
                if form.is_valid():
                    form.save(user=request.user)
        # Create new filterset if pk not provided
        else:
            form = forms.UserListForm(form_dict)
            if form.is_valid():
                print('valid')
                filterset_object = form.save(user=request.user)
                print(filterset_object)
            else:
                print(form.errors)
    # Get the objects associated to the current user
    filterset_objects = request.user.filtersets.all()
    filtersets = []
    for filterset in filterset_objects:
        filtersets.append({
            "title": filterset.title or '',
            "filters": filterset.filters,
            "pk": filterset.pk,
        })
    data = {
        'filtersets': filtersets,
        'pk': filterset_object.pk if filterset_object else None
    }
    return JsonResponse(data)

# Gets a fields options
def FilterInput(request):
    if not request.user.is_authenticated:
        raise Http404()
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
    if not request.user.is_authenticated:
        raise Http404()
    tools_form = forms.ProfilesToolsForm(request.POST)
    if tools_form.is_valid():
        tool_inputs = tools_form.cleaned_data
        sorted_profiles = get_profiles(tool_inputs, request.user)
        output = create_excel(tool_inputs, sorted_profiles)
        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        return response
