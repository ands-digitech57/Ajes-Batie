from pathlib import Path
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from cloudinary.models import CloudinaryField
from .validators import validate_cv_file


def safe_file_url(file_value):
    if file_value is None:
        return ''
    raw_value = None
    for attr in ('public_id', 'name'):
        try:
            raw_value = getattr(file_value, attr, None)
        except Exception:
            raw_value = None
        if raw_value:
            break
    if not raw_value:
        try:
            raw_value = str(file_value)
        except Exception:
            raw_value = ''
    if not raw_value or raw_value == 'None':
        return ''

    raw_text = str(raw_value).replace('\\', '/')
    if not raw_text.startswith(('http://', 'https://')):
        local_path = Path(settings.MEDIA_ROOT) / raw_text
        if local_path.exists():
            return f"{settings.MEDIA_URL}{raw_text}"

    try:
        return file_value.url
    except Exception:
        return ''


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

    @property
    def uploaded_photo_url(self):
        return safe_file_url(self.photo_file)

    @property
    def cv_url_safe(self):
        return safe_file_url(self.cv_file)

    @property
    def get_avatar_url(self):
        return self.uploaded_photo_url or self.photo_url or f"https://ui-avatars.com/api/?name={self.display_name}&background=10b981&color=fff"

    def get_absolute_url(self):
        return reverse('profiles:detail', kwargs={'pk': self.pk})
