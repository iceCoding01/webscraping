from django.core.management.base import BaseCommand
from scholarships.scrapers.api_scraper import APIScholarshipScraper
from scholarships.models import Scholarship
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run API-based scholarship scrapers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--field',
            help='Field of study to filter by',
            default=None
        )
        parser.add_argument(
            '--country',
            help='Country to filter by',
            default=None
        )
        parser.add_argument(
            '--pages',
            type=int,
            help='Number of pages to scrape from CORDIS',
            default=1
        )

    def handle(self, *args, **options):
        scraper = APIScholarshipScraper()
        field = options.get('field')
        country = options.get('country')
        pages = options.get('pages', 1)

        self.stdout.write(self.style.SUCCESS('Starting API-based scholarship scraping...'))
        
        try:
            scholarships = scraper.scrape_scholarships(
                field_of_study=field,
                country=country,
                num_pages=pages
            )
            
            count = 0
            for data in scholarships:
                scholarship, created = Scholarship.objects.update_or_create(
                    title=data['title'],
                    organization=data['organization'],
                    source_website=data['source_website'],
                    defaults={
                        'description': data['description'],
                        'requirements': data['requirements'],
                        'amount': data['amount'],
                        'country': data['country'],
                        'education_level': data['education_level'],
                        'field_of_study': data['field_of_study'],
                        'deadline': data['deadline'],
                        'website_url': data['website_url'],
                        'is_fully_funded': data['is_fully_funded'],
                        'is_active': data['is_active']
                    }
                )
                
                if created:
                    logger.info(f'Created new scholarship: {scholarship.title}')
                    count += 1
                else:
                    logger.info(f'Updated existing scholarship: {scholarship.title}')

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully scraped {count} new scholarships!'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during scraping: {str(e)}')
            )
            logger.error(f'Scraping error: {str(e)}', exc_info=True)