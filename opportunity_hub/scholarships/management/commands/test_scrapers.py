import logging
from django.core.management.base import BaseCommand
from scholarships.scrapers.scholarships_positions_scraper import ScholarshipsPositionsPortalScraper
from scholarships.scrapers.university_positions_scraper import UniversityPositionsScraper
import time

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test scholarship scrapers by running them and printing results'

    def handle(self, *args, **options):
        # Increase logging for debugging
        logging.basicConfig(level=logging.INFO)
        
        scrapers = [
            ScholarshipsPositionsPortalScraper(),
            UniversityPositionsScraper()
        ]

        for scraper in scrapers:
            self.stdout.write(f"\nTesting {scraper.__class__.__name__}...")
            
            try:
                # First check if we can access the site's homepage
                if isinstance(scraper, ScholarshipsPositionsPortalScraper):
                    url = 'https://scholarship-positions.com'
                else:  # UniversityPositions
                    url = 'https://www.universitypositions.eu'
                
                self.stdout.write(f"Accessing {url}...")
                scraper.driver.get(url)
                time.sleep(5)  # Wait for any redirects/blocks
                
                # Log current state
                self.stdout.write(f"Page title: {scraper.driver.title}")
                self.stdout.write(f"Current URL: {scraper.driver.current_url}")
                
                # Check for common blocking indicators
                page_source = scraper.driver.page_source.lower()
                if "captcha" in page_source:
                    self.stdout.write(self.style.WARNING("Detected CAPTCHA!"))
                if "blocked" in page_source:
                    self.stdout.write(self.style.WARNING("Access might be blocked!"))
                if "robot" in page_source or "automated" in page_source:
                    self.stdout.write(self.style.WARNING("Bot detection message found!"))
                
                # Try scraping with debug info
                self.stdout.write("Attempting to scrape scholarships...")
                scholarships = scraper.scrape_scholarships(num_pages=1)
                
                self.stdout.write(f"Successfully scraped {len(scholarships)} scholarships")
                
                if scholarships:
                    self.stdout.write("\nFirst scholarship details:")
                    for key, value in scholarships[0].items():
                        self.stdout.write(f"{key}: {value}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
                continue
                
            finally:
                # Save the page source for debugging
                try:
                    with open(f'debug_{scraper.__class__.__name__}.html', 'w', encoding='utf-8') as f:
                        f.write(scraper.driver.page_source)
                    self.stdout.write(f"Saved page source to debug_{scraper.__class__.__name__}.html")
                except Exception as e:
                    self.stdout.write(f"Could not save debug file: {str(e)}")
            
            self.stdout.write(self.style.SUCCESS(f"{scraper.__class__.__name__} test completed"))
            
        self.stdout.write(self.style.SUCCESS('\nAll scraper tests completed'))