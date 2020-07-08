from django.urls import path
from . import views


urlpatterns = [
    path('',views.Learning.as_view(),name='learning'),
    path('models', views.LearningModels.as_view(), name='learning-models'),
    path('files', views.LearningFiles.as_view(), name='learning-files'),
]
