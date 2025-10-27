from celery import shared_task
from .utils.scraper import ScholarshipScraper
from .models import Scholarship
from django.utils import timezone

@shared_task
def scrape_scholarships_task():
    """Celery task to scrape scholarships from various sources"""
    scraper = ScholarshipScraper()
    
    # Scrape from multiple sources
    scholarships_com = scraper.scrape_scholarships_com()
    fulbright = scraper.scrape_fulbright()
    erasmus = scraper.scrape_erasmus()
    
    # Combine all scholarships
    all_scholarships = scholarships_com + fulbright + erasmus
    
    # Save to database
    for scholarship_data in all_scholarships:
        Scholarship.objects.create(**scholarship_data)
    
    return f"Successfully scraped {len(all_scholarships)} scholarships."

@shared_task
def clean_expired_scholarships_task():
    """Clean up expired scholarship listings"""
    today = timezone.now().date()
    expired_scholarships = Scholarship.objects.filter(deadline__lt=today)
    deleted_count = expired_scholarships.count()
    expired_scholarships.delete()
    
    return f"Cleaned up {deleted_count} expired scholarship listings."