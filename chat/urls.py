from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('<int:recipient_id>/', views.inbox, name='inbox_with_user'),
]