from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.meetings, name='meetings'),
    path('get-meetings', views.get_meetings, name='get-meetings'),
]
