from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify  # <-- 1. AJOUTEZ CETTE LIGNE TOUT EN HAUT

class JournalPost(models.Model):
    CATEGORY_CHOICES = [
        ('activity', 'Activite'),
        ('event', 'Evenement'),
        ('announcement', 'Annonce'),
        ('project', 'Projet'),
        ('report', 'Compte rendu'),
    ]

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_posts')
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)  # <-- 2. AJOUTEZ CE CHAMP
    summary = models.TextField(blank=True)
    content = models.TextField()
    image_url = models.URLField(blank=True)
    image_file = models.FileField(upload_to='journal_images/', null=True, blank=True)
    video_file = models.FileField(upload_to='journal_videos/', null=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='activity')
    event_date = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-event_date', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('journal:detail', kwargs={'slug': self.slug})

    @property
    def likes_count(self):
        return self.likes.count()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class JournalPostLike(models.Model):
    post = models.ForeignKey(JournalPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} aime {self.post}'


class JournalPostComment(models.Model):
    post = models.ForeignKey(JournalPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user} commente {self.post}'
