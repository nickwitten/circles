from django.urls import path
from . import views


urlpatterns = [
    path('',views.Learning.as_view(),name='learning'),
    path('programming',views.Learning.as_view(),name='learning-programming'),
    path('theme',views.Learning.as_view(),name='learning-theme'),
    path('module',views.Learning.as_view(),name='learning-module'),
    path('models', views.LearningModels.as_view(), name='learning-models'),
    path('completed', views.MembersCompleted.as_view(), name='members-completed'),
    path('schedule', views.LearningSchedule.as_view(), name='learning-schedule'),
]
