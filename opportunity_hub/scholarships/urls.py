from django.urls import path
from . import views

app_name = 'scholarships'

urlpatterns = [
    path('', views.scholarship_list, name='scholarship-list'),
    path('<int:pk>/', views.scholarship_detail, name='scholarship-detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('apply/<int:pk>/', views.scholarship_apply, name='scholarship-apply'),
]