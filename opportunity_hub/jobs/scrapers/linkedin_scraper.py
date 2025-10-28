from .base import BaseScraper
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    def scrape_jobs(self, keywords=None, location=None, num_pages=1):
        """
        Scrape jobs from LinkedIn
        """
        jobs = []
        keywords = keywords or "all"
        
        try:
            for page in range(num_pages):
                start = page * 25  # LinkedIn uses multiples of 25 for pagination
                url = f'https://www.linkedin.com/jobs/search?keywords={keywords}&start={start}'
                if location:
                    url += f'&location={location}'
                
                self.driver.get(url)
                self.wait_for_element(By.CLASS_NAME, 'base-search-card')
                self.scroll_page()
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                job_cards = soup.find_all('div', class_='base-search-card')
                
                for card in job_cards:
                    try:
                        # Extract salary range if available
                        salary_elem = card.find('span', class_='job-search-card__salary-info')
                        salary_range = salary_elem.text.strip() if salary_elem else None

                        # Determine if job is remote
                        workplace_elem = card.find('span', class_='workplace-type')
                        is_remote = workplace_elem and 'remote' in workplace_elem.text.lower()

                        job = {
                            'title': card.find('h3', class_='base-search-card__title').text.strip(),
                            'company': card.find('h4', class_='base-search-card__subtitle').text.strip(),
                            'location': card.find('span', class_='job-search-card__location').text.strip(),
                            'employment_type': self._determine_employment_type(card),
                            'description': self._extract_description(card),
                            'requirements': self._extract_requirements(card),
                            'salary_range': salary_range,
                            'application_url': card.find('a', class_='base-card__full-link')['href'],
                            'source_website': 'LinkedIn',
                            'posted_date': self._extract_date(card),
                            'is_remote': is_remote,
                            'is_active': True
                        }
                        jobs.append(job)
                        
                    except Exception as e:
                        logger.error(f"Error extracting LinkedIn job data: {str(e)}")
                        continue

        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {str(e)}")
        
        return jobs

    def _determine_employment_type(self, card):
        """Determine employment type from job card"""
        job_types = {
            'full-time': 'FULL_TIME',
            'part-time': 'PART_TIME',
            'contract': 'CONTRACT',
            'internship': 'INTERNSHIP',
            'remote': 'REMOTE'
        }
        
        type_elem = card.find('span', class_='job-search-card__employment-type')
        if not type_elem:
            return 'FULL_TIME'  # Default to full-time if not specified
            
        text = type_elem.text.lower()
        for key, value in job_types.items():
            if key in text:
                return value
                
        return 'FULL_TIME'

    def _extract_description(self, card):
        """Extract job description"""
        desc_elem = card.find('p', class_='base-search-card__metadata')
        return desc_elem.text.strip() if desc_elem else "No description available"

    def _extract_requirements(self, card):
        """Extract requirements from job description"""
        # Click on job card to load full description
        try:
            job_link = card.find('a', class_='base-card__full-link')['href']
            self.driver.execute_script(f"window.open('{job_link}', '_blank');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            self.wait_for_element(By.CLASS_NAME, 'description__text')
            description = self.driver.find_element(By.CLASS_NAME, 'description__text').text
            
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            # Extract requirements section
            lines = description.split('\n')
            requirements = []
            capturing = False
            
            for line in lines:
                if any(word in line.lower() for word in ['required', 'requirements', 'qualifications']):
                    capturing = True
                    requirements.append(line.strip())
                elif capturing and line.strip():
                    if any(word in line.lower() for word in ['about us', 'benefits', 'what we offer']):
                        break
                    requirements.append(line.strip())
                    
            return '\n'.join(requirements) if requirements else "No specific requirements listed"
            
        except Exception as e:
            logger.error(f"Error extracting LinkedIn job requirements: {str(e)}")
            return "Error loading requirements"

    def _extract_date(self, card):
        """Extract and parse posting date"""
        date_elem = card.find('time', class_='job-search-card__listdate')
        if not date_elem:
            return timezone.now()
            
        try:
            # LinkedIn usually shows relative dates like "3 days ago"
            date_text = date_elem.text.strip().lower()
            if 'hour' in date_text:
                hours = int(date_text.split()[0])
                return timezone.now() - timezone.timedelta(hours=hours)
            elif 'day' in date_text:
                days = int(date_text.split()[0])
                return timezone.now() - timezone.timedelta(days=days)
            elif 'week' in date_text:
                weeks = int(date_text.split()[0])
                return timezone.now() - timezone.timedelta(weeks=weeks)
            elif 'month' in date_text:
                months = int(date_text.split()[0])
                return timezone.now() - timezone.timedelta(days=months*30)
            else:
                return timezone.now()
        except Exception:
            return timezone.now()