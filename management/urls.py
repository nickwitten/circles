from django.urls import path
from . import views


urlpatterns = [
    path('',views.Management.as_view(),name='management'),
]
