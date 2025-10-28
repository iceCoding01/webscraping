from .base import BaseScraper
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class GlassdoorScraper(BaseScraper):
    def scrape_jobs(self, keywords=None, location=None, num_pages=1):
        """
        Scrape jobs from Glassdoor
        """
        jobs = []
        keywords = keywords or "all"
        location = location or "remote"
        
        try:
            for page in range(num_pages):
                url = f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keywords}&locT=C&locId=1'
                if page > 0:
                    url += f'&p={page+1}'
                
                self.driver.get(url)
                self.wait_for_element(By.CLASS_NAME, 'jobCard')
                self.scroll_page()
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                job_cards = soup.find_all('li', class_='jobCard')
                
                for card in job_cards:
                    try:
                        # Extract salary range if available
                        salary_elem = card.find('span', {'data-test': 'detailSalary'})
                        salary_range = salary_elem.text.strip() if salary_elem else None

                        # Determine if job is remote
                        location_elem = card.find('span', {'data-test': 'location'})
                        is_remote = location_elem and 'remote' in location_elem.text.lower()

                        job = {
                            'title': card.find('a', {'data-test': 'job-link'}).text.strip(),
                            'company': card.find('div', {'data-test': 'employer-name'}).text.strip(),
                            'location': location_elem.text.strip() if location_elem else 'Not specified',
                            'employment_type': self._determine_employment_type(card),
                            'description': self._extract_description(card),
                            'requirements': self._extract_requirements(card),
                            'salary_range': salary_range,
                            'application_url': 'https://www.glassdoor.com' + card.find('a', {'data-test': 'job-link'})['href'],
                            'source_website': 'Glassdoor',
                            'posted_date': self._extract_date(card),
                            'is_remote': is_remote,
                            'is_active': True
                        }
                        jobs.append(job)
                        
                    except Exception as e:
                        logger.error(f"Error extracting Glassdoor job data: {str(e)}")
                        continue

        except Exception as e:
            logger.error(f"Error scraping Glassdoor: {str(e)}")
        
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
        
        type_elem = card.find('span', {'data-test': 'job-type'})
        if not type_elem:
            return 'FULL_TIME'  # Default to full-time if not specified
            
        text = type_elem.text.lower()
        for key, value in job_types.items():
            if key in text:
                return value
                
        return 'FULL_TIME'

    def _extract_description(self, card):
        """Extract job description by clicking on the job card"""
        try:
            job_link = card.find('a', {'data-test': 'job-link'})['href']
            self.driver.execute_script(f"window.open('https://www.glassdoor.com{job_link}', '_blank');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            self.wait_for_element(By.CLASS_NAME, 'jobDescriptionContent')
            description = self.driver.find_element(By.CLASS_NAME, 'jobDescriptionContent').text
            
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return description
            
        except Exception as e:
            logger.error(f"Error extracting Glassdoor job description: {str(e)}")
            return "Error loading description"

    def _extract_requirements(self, card):
        """Extract requirements from job description"""
        description = self._extract_description(card)
        
        # Look for requirements section
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

    def _extract_date(self, card):
        """Extract and parse posting date"""
        date_elem = card.find('div', {'data-test': 'job-age'})
        if not date_elem:
            return timezone.now()
            
        try:
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