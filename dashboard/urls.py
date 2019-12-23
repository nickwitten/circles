from django.urls import path
from . import views
from .views import DashboardListView

urlpatterns = [
    path('',views.DashboardListView.as_view(),name='dashboard')
]
