
from django.db import models
from .models import CustomUser

class ArtisanAccessCode(models.Model):
    artisan = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='access_codes')
    code = models.CharField(max_length=50, help_text="Alternative password/access code")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Code for {self.artisan.username}"
