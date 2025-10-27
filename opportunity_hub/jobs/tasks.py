from celery import shared_task
from .utils.scraper import JobScraper
from .models import JobListing
from django.utils import timezone

@shared_task
def scrape_jobs_task():
    """Celery task to scrape jobs from various sources"""
    scraper = JobScraper()
    
    # Scrape from multiple sources
    indeed_jobs = scraper.scrape_indeed()
    linkedin_jobs = scraper.scrape_linkedin()
    remote_jobs = scraper.scrape_remoteok()
    
    # Combine all jobs
    all_jobs = indeed_jobs + linkedin_jobs + remote_jobs
    
    # Save to database
    for job_data in all_jobs:
        JobListing.objects.create(**job_data)
    
    return f"Successfully scraped {len(all_jobs)} jobs."

@shared_task
def clean_old_jobs_task():
    """Clean up old job listings"""
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    old_jobs = JobListing.objects.filter(created_at__lt=thirty_days_ago)
    deleted_count = old_jobs.count()
    old_jobs.delete()
    
    return f"Cleaned up {deleted_count} old job listings."