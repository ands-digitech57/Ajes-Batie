from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_list, name='list'),
    path('modifier/', views.profile_edit, name='edit'),
    path('<int:pk>/', views.profile_detail, name='detail'),
]
