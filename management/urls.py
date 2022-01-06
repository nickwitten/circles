from django.urls import path
from . import views


urlpatterns = [
    path('',views.Management.as_view(),name='management'),
    path('user-info',views.UserInfo.as_view(),name='create-user'),
    path('user-info/<int:pk>',views.UserInfo.as_view(),name='update-user'),
    path('delete-user/<int:pk>',views.UserInfo.as_view(),name='delete-user'),
    path('chapter',views.CreateChapterView.as_view(),name='create-chapter'),
    path('chapter/<int:pk>',views.UpdateChapterView.as_view(),name='update-chapter'),
    path('delete-chapter/<int:pk>',views.DeleteChapterView.as_view(),name='delete-chapter'),
    path('site',views.CreateSiteView.as_view(),name='create-site'),
    path('site/<int:pk>',views.UpdateSiteView.as_view(),name='update-site'),
    path('delete-site/<int:pk>',views.DeleteSiteView.as_view(),name='delete-site'),
]
