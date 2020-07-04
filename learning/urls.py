from django.urls import path
from . import views


urlpatterns = [
    path('',views.Learning.as_view(),name='learning')
]
