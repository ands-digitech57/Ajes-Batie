from django.contrib.auth.models import User
from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        JOB = "job", "Offre d'emploi"
        JOURNAL = "journal", "Journal"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_index=True,
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField(
        blank=True,
    )

    link = models.URLField(
        blank=True,
    )

    type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
    )

    is_read = models.BooleanField(
        default=False,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]

        verbose_name = "Notification"

        verbose_name_plural = "Notifications"

        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} | {self.title}"