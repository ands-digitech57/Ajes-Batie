from django.db import models
from django.urls import reverse
from cloudinary.models import CloudinaryField  # Importation essentielle

class JobOffer(models.Model):
    CONTRACT_CHOICES = [
        ('full_time', 'Temps plein'),
        ('part_time', 'Temps partiel'),
        ('internship', 'Stage'),
        ('mission', 'Mission'),
        ('apprenticeship', 'Apprentissage'),
        ('other', 'Autre'),
    ]

    title = models.CharField(max_length=180)
    description = models.TextField()
    company_name = models.CharField(max_length=180)
    recruiter_name = models.CharField(max_length=140)
    recruiter_phone = models.CharField(max_length=30)
    recruiter_email = models.EmailField(blank=True)
    location = models.CharField(max_length=140, blank=True)
    contract_type = models.CharField(max_length=30, choices=CONTRACT_CHOICES, default='mission')
    required_skills = models.TextField(blank=True)
    
    # NOUVEAUX CHAMPS MÉDIAS POUR LES OFFRES
    image_file = models.ImageField(upload_to='job_images/', null=True, blank=True)
    video_file = models.FileField(upload_to='job_videos/', null=True, blank=True)
    
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.pk})


class Application(models.Model):
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='applications')
    profile = models.ForeignKey('profiles.Profile', on_delete=models.CASCADE, related_name='applications')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['job_offer', 'profile'], name='unique_job_application')
        ]

    def __str__(self):
        return f'{self.profile} -> {self.job_offer}'