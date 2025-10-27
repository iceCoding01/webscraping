from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Additional fields for user profile
    bio = models.TextField(max_length=500, blank=True)
    education_level = models.CharField(max_length=50, blank=True)
    field_of_interest = models.CharField(max_length=100, blank=True)
    preferred_job_type = models.CharField(max_length=50, blank=True)
    preferred_location = models.CharField(max_length=100, blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    job_alert_keywords = models.CharField(max_length=200, blank=True)
    scholarship_alert_keywords = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['username']