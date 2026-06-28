from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from cloudinary.models import CloudinaryField
from .validators import validate_cv_file

class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Profile(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Disponible"
        EMPLOYED = "employed", "En activité"
        STUDENT = "student", "Étudiant"
        UNAVAILABLE = "unavailable", "Non disponible"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=150, blank=True)
    current_company = models.CharField(max_length=150, blank=True)
    industry = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, related_name="profiles", blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    education_level = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Correction : Champ Cloudinary initialisé proprement pour l'image
    photo_file = CloudinaryField('image', blank=True, null=True)
    
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
        return self.user.get_full_name() or self.user.username

    @property
    def public_phone(self):
        return self.whatsapp or self.phone

    # Code Sécurisé : Retourne l'URL Cloudinary ou un avatar UI gratuit si vide
    @property
    def get_avatar_url(self):
        if self.photo_file and hasattr(self.photo_file, 'url'):
            return self.photo_file.url
        elif self.photo_url:
            return self.photo_url
        return f"https://ui-avatars.com/api/?name={self.display_name}&background=10b981&color=fff"

    def get_absolute_url(self):
        return reverse('profiles:detail', kwargs={'pk': self.pk})