from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.post_list, name='list'),
    path('publier/', views.post_create, name='create'),
    path('aimer/<slug:slug>/', views.post_like, name='like'),
    path('<slug:slug>/', views.post_detail, name='detail'),
]
