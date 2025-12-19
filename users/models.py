from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_artisan = models.BooleanField(default=False, help_text="Designates whether this user is an artisan/maker.")
    bio = models.TextField(blank=True, help_text="Short bio for the artisan.")
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_artisan']),
        ]

    def __str__(self):
        return self.username

    def get_display_name(self):
        """Return full name if available, otherwise username"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
