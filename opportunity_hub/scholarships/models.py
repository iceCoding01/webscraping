from django.db import models
from django.urls import reverse

class Scholarship(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('UNDERGRADUATE', 'Undergraduate'),
        ('MASTERS', 'Masters'),
        ('PHD', 'PhD'),
        ('POSTDOC', 'Post-Doctoral'),
        ('ALL', 'All Levels'),
    ]

    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    amount = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVEL_CHOICES)
    deadline = models.DateField()
    website_url = models.URLField()
    source_website = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=200)
    is_fully_funded = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.organization}"

    def get_absolute_url(self):
        return reverse('scholarships:scholarship-detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title', 'organization']),
            models.Index(fields=['country']),
            models.Index(fields=['education_level']),
            models.Index(fields=['deadline']),
        ]

class ScholarshipApplication(models.Model):
    STATUS_CHOICES = [
        ('SAVED', 'Saved'),
        ('APPLIED', 'Applied'),
        ('IN_PROGRESS', 'In Progress'),
        ('REJECTED', 'Rejected'),
        ('ACCEPTED', 'Accepted'),
    ]

    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SAVED')
    notes = models.TextField(blank=True)
    applied_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.scholarship.title}"

    class Meta:
        unique_together = ('user', 'scholarship')
