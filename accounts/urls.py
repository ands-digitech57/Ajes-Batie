from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import reverse_lazy
from . import views

app_name = 'accounts'

urlpatterns = [
    path('inscription/', views.signup, name='signup'),
    path('tableau-de-bord/', views.dashboard, name='dashboard'),
    path('notifications/', views.notifications, name='notifications'),
    path('connexion/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    path('mot-de-passe-oublie/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.txt',
        html_email_template_name='registration/password_reset_email.html',
        success_url=reverse_lazy('accounts:password_reset_done'),
    ), name='password_reset'),
    path('mot-de-passe-envoye/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reinitialiser/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete'),
    ), name='password_reset_confirm'),
    path('mot-de-passe-reinitialise/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]
