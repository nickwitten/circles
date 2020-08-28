from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.meetings, name='meetings'),
    path('get-meetings', views.get_meetings, name='get-meetings'),
    path('get-meeting-info', views.get_meeting_info, name='get-meeting-info'),
    path('post-meeting-info/<int:pk>', views.post_meeting_info, name='post-meeting-info'),
    path('delete/<int:pk>', views.delete_meeting, name='delete-meeting'),
    path('get-members', views.get_members, name='get-members'),
]
