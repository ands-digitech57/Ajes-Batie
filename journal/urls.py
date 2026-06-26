from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    # Le double nomnage règle définitivement le crash NoReverseMatch sur tout ton site
    path('', views.post_list, name='post_list'),
    path('', views.post_list, name='list'), 
    path('creer/', views.post_create, name='post_create'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
    path('<slug:slug>/like/', views.post_like, name='post_like'),
]