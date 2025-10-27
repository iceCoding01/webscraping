from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job-list'),
    path('<int:pk>/', views.job_detail, name='job-detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('apply/<int:pk>/', views.job_apply, name='job-apply'),
]