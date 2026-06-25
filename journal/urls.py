from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('creer/', views.post_create, name='post_create'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
    path('<slug:slug>/like/', views.post_like, name='post_like'),
]