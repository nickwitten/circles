from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('',views.profiles,name='profiles'),
    path('create_profile/',views.create_profile,name='create-profile'),
    path('profile/<int:pk>/',views.ProfileDetailView.as_view(),name='profile-detail'),
    path('profile/<int:pk>/update',views.ProfileUpdateView.as_view(),name='profile-update'),
    path('profile/<int:pk>/delete',views.ProfileDeleteView.as_view(), name='profile-delete'),
    path('profile/<int:pk>/update/residence', views.ResidenceCreateView.as_view(), name='create-residence'),
    path('profile/residence/<int:pk>/update',views.ResidenceUpdateView.as_view(),name='update-residence'),
    path('profile/residence/delete/<int:pk>',views.ResidenceDeleteView.as_view(),name='delete-residence'),
    path('profile/<int:pk>/update/role', views.RoleCreateView.as_view(), name='create-role'),
    path('profile/role/<int:pk>/update',views.RoleUpdateView.as_view(),name='update-role'),
    path('profile/role/delete/<int:pk>',views.RoleDeleteView.as_view(),name='delete-role'),
    path('profile/<int:pk>/update/training', views.TrainingAddView.as_view(), name='add-training'),
    path('profile/training/<int:pk>/update',views.TrainingUpdateView.as_view(),name='update-training'),
    path('profile/training/delete/<int:pk>',views.TrainingDeleteView.as_view(),name='delete-training'),
    path('profile/<int:pk>/update/childrenedit', views.ChildrenEditView.as_view(), name='edit-children'),
    path('profile/<int:pk>/update/childrenedit/childinfo',views.ChildInfoCreateView.as_view(), name='create-childinfo'),
    path('profile/childinfo/<int:pk>/update',views.ChildInfoUpdateView.as_view(), name='update-childinfo'),
    path('profile/childinfo/<int:pk>/delete',views.ChildInfoDeleteView.as_view(), name='delete-childinfo'),
    path('profile/childinfo/<int:pk>/child', views.ChildCreateView.as_view(), name='create-child'),
    path('profile/childinfo/child/<int:pk>/update',views.ChildUpdateView.as_view(),name='update-child'),
    path('profile/childinfo/child/<int:pk>/delete',views.ChildDeleteView.as_view(),name='delete-child'),
    path('profile/get-profiles',views.GetProfiles,name='get-profiles'),
    path('profile/filtersets',views.UserFiltersets,name='filtersets'),
    path('profile/get-filterinput',views.FilterInput,name='get-filterinput'),
    path('profile/get-profiles-excel',views.ExcelDump,name='get-profiles-excel'),
]
