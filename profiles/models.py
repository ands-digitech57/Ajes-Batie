from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from .validators import validate_image_file, validate_cv_file


class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Profile(models.Model):
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('employed', 'En activite'),
        ('student', 'Etudiant'),
        ('unavailable', 'Non disponible'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=150, blank=True)
    current_company = models.CharField(max_length=150, blank=True)
    industry = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    education_level = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    linkedin_url = models.URLField(blank=True)
    photo_file = models.FileField(upload_to='profile_photos/', blank=True, null=True, validators=[validate_image_file])
    cv_file = models.FileField(upload_to='cvs/', blank=True, null=True, validators=[validate_cv_file])
    photo_url = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name', 'user__username']

    def __str__(self):
        full_name = f'{self.user.first_name} {self.user.last_name}'.strip()
        return full_name or self.user.username

    @property
    def display_name(self):
        full_name = f'{self.user.first_name} {self.user.last_name}'.strip()
        return full_name or self.user.username

    @property
    def public_phone(self):
        return self.whatsapp or self.phone

    def get_absolute_url(self):
        return reverse('profiles:detail', kwargs={'pk': self.pk})
