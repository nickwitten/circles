from django.urls import path
from django.conf.urls import url
from . import views
from .views import ProfileListView, ProfileCreateView, ProfileDetailView, ProfileDeleteView, ProfileUpdateView, update_profile, create_profile, ResidenceCreateView, ResidenceUpdateView, ResidenceDeleteView, RoleCreateView, RoleUpdateView, RoleDeleteView, TrainingAddView, TrainingUpdateView, TrainingDeleteView, ChildCreateView, ChildUpdateView, ChildrenEditView, ChildInfoCreateView, profiles, GetProfiles, CreateFilterset,GetFiltersets,AddFiltersetTitle,DeleteFilterset,FilterInput

urlpatterns = [
    #path('',ProfileListView.as_view(),name='profiles'),
    path('',profiles,name='profiles'),
    path('create_profile/',ProfileCreateView.as_view(),name='create-profile'),
    path('profile/<int:pk>/',ProfileDetailView.as_view(),name='profile-detail'),
    path('profile/<int:pk>/update',ProfileUpdateView.as_view(),name='profile-update'),
    path('profile/<int:pk>/delete',ProfileDeleteView.as_view(), name='profile-delete'),
    path('profile/<int:pk>/update/residence', ResidenceCreateView.as_view(), name='create-residence'),
    path('profile/residence/<int:pk>/update',ResidenceUpdateView.as_view(),name='update-residence'),
    path('profile/residence/delete/<int:pk>',ResidenceDeleteView.as_view(),name='delete-residence'),
    path('profile/<int:pk>/update/role', RoleCreateView.as_view(), name='create-role'),
    path('profile/role/<int:pk>/update',RoleUpdateView.as_view(),name='update-role'),
    path('profile/role/delete/<int:pk>',RoleDeleteView.as_view(),name='delete-role'),
    path('profile/<int:pk>/update/training', TrainingAddView.as_view(), name='add-training'),
    path('profile/training/<int:pk>/update',TrainingUpdateView.as_view(),name='update-training'),
    path('profile/training/delete/<int:pk>',TrainingDeleteView.as_view(),name='delete-training'),
    path('profile/<int:pk>/update/childrenedit', ChildrenEditView, name='edit-children'),
    path('profile/<int:pk>/update/childrenedit/childinfo',ChildInfoCreateView.as_view(), name='create-childinfo'),
    path('profile/childinfo/<int:pk>/child', ChildCreateView.as_view(), name='create-child'),
    path('profile/childinfo/child/<int:pk>/update',ChildUpdateView.as_view(),name='update-child'),
    path('profile/get-profiles',GetProfiles,name='get-profiles'),
    path('profile/create-filterset',CreateFilterset,name='create-filterset'),
    path('profile/get-filtersets',GetFiltersets,name='get-filtersets'),
    path('profile/add-filterset-title',AddFiltersetTitle,name='add-filterset-title'),
    path('profile/delete-filterset',DeleteFilterset,name='delete-filterset'),
    path('profile/get-filterinput',FilterInput,name='get-filterinput'),
]
