from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_artisan = models.BooleanField(default=False, help_text="Designates whether this user is an artisan/maker.")
    bio = models.TextField(blank=True, help_text="Short bio for the artisan.")
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    vacation_mode = models.BooleanField(default=False, help_text="Temporarily disable products from showing in the marketplace.")
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Contact number for orders.")
    payment_qr_code = models.ImageField(upload_to='payment_qrs/', blank=True, null=True, help_text="QR Code for receiving payments.")

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

class ArtisanAccessCode(models.Model):
    artisan = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='access_codes')
    code = models.CharField(max_length=50, help_text="Alternative password/access code")
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100, blank=True, help_text="Who is this code for?")

    def __str__(self):
        return f"{self.code} ({self.artisan.username})"
