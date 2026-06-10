from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
    path('publier/', views.job_create, name='create'),
    path('<int:pk>/', views.job_detail, name='detail'),
    path('<int:pk>/postuler/', views.job_apply, name='apply'),
]
