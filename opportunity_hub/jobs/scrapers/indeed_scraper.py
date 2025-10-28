from .base import BaseScraper
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class IndeedScraper(BaseScraper):
    def scrape_jobs(self, keywords=None, location=None, num_pages=1):
        """
        Scrape jobs from Indeed
        """
        jobs = []
        keywords = keywords or "all"
        location = location or "remote"
        
        try:
            for page in range(num_pages):
                start = page * 10  # Indeed uses multiples of 10 for pagination
                url = f'https://www.indeed.com/jobs?q={keywords}&l={location}&start={start}'
                
                self.driver.get(url)
                self.wait_for_element(By.CLASS_NAME, 'job_seen_beacon')
                self.scroll_page()
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards:
                    try:
                        # Extract salary range if available
                        salary_elem = card.find('div', class_='salary-snippet-container')
                        salary_range = salary_elem.text.strip() if salary_elem else None

                        # Determine if job is remote
                        location_elem = card.find('div', class_='companyLocation')
                        is_remote = 'remote' in location_elem.text.lower() if location_elem else False

                        job = {
                            'title': card.find('h2', class_='jobTitle').text.strip(),
                            'company': card.find('span', class_='companyName').text.strip(),
                            'location': location_elem.text.strip() if location_elem else 'Not specified',
                            'employment_type': self._determine_employment_type(card),
                            'description': card.find('div', class_='job-snippet').text.strip(),
                            'requirements': self._extract_requirements(card),
                            'salary_range': salary_range,
                            'application_url': 'https://indeed.com' + card.find('a', class_='jcs-JobTitle')['href'],
                            'source_website': 'Indeed',
                            'posted_date': timezone.now(),  # Indeed doesn't always show exact dates
                            'is_remote': is_remote,
                            'is_active': True
                        }
                        jobs.append(job)
                        
                    except Exception as e:
                        logger.error(f"Error extracting Indeed job data: {str(e)}")
                        continue

        except Exception as e:
            logger.error(f"Error scraping Indeed: {str(e)}")
        
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
        
        metadata = card.find('div', class_='metadata')
        if not metadata:
            return 'FULL_TIME'  # Default to full-time if not specified
            
        text = metadata.text.lower()
        for key, value in job_types.items():
            if key in text:
                return value
                
        return 'FULL_TIME'

    def _extract_requirements(self, card):
        """Extract requirements from job description"""
        description = card.find('div', class_='job-snippet')
        if not description:
            return "No specific requirements listed"
            
        text = description.text.strip()
        # Look for common requirement indicators
        requirements = []
        if 'required' in text.lower() or 'requirements' in text.lower():
            # Split by common delimiters and clean up
            for line in text.split('\n'):
                if any(word in line.lower() for word in ['required', 'requirements', 'qualifications', 'must have']):
                    requirements.append(line.strip())
                    
        return '\n'.join(requirements) if requirements else text