from .base import BaseScraper
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class RemoteOKScraper(BaseScraper):
    def scrape_jobs(self, keywords=None, location=None, num_pages=1):
        """
        Scrape jobs from RemoteOK
        Note: RemoteOK focuses on remote jobs, so location parameter is ignored
        """
        jobs = []
        keywords = keywords or "all"
        
        try:
            url = f'https://remoteok.com/remote-{keywords}-jobs'
            self.driver.get(url)
            self.wait_for_element(By.TAG_NAME, 'tr')
            self.scroll_page()
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            job_rows = soup.find_all('tr', class_='job')
            
            for row in job_rows:
                try:
                    # Extract salary range if available
                    salary_elem = row.find('div', class_='location')
                    salary_range = None
                    if salary_elem:
                        salary_text = salary_elem.text.strip()
                        if '$' in salary_text:
                            salary_range = salary_text

                    job = {
                        'title': row.find('h2', itemprop='title').text.strip(),
                        'company': row.find('h3', itemprop='name').text.strip(),
                        'location': 'Remote',  # All jobs are remote
                        'employment_type': self._determine_employment_type(row),
                        'description': self._extract_description(row),
                        'requirements': self._extract_requirements(row),
                        'salary_range': salary_range,
                        'application_url': 'https://remoteok.com' + row.find('a', class_='job')['href'],
                        'source_website': 'RemoteOK',
                        'posted_date': self._extract_date(row),
                        'is_remote': True,  # All jobs are remote
                        'is_active': True
                    }
                    jobs.append(job)
                    
                except Exception as e:
                    logger.error(f"Error extracting RemoteOK job data: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {str(e)}")
        
        return jobs

    def _determine_employment_type(self, row):
        """Determine employment type from job row"""
        tags = row.find_all('td', class_='tags')
        if not tags:
            return 'FULL_TIME'  # Default to full-time

        text = ' '.join(tag.text.lower() for tag in tags)
        
        if 'full time' in text or 'fulltime' in text:
            return 'FULL_TIME'
        elif 'part time' in text or 'parttime' in text:
            return 'PART_TIME'
        elif 'contract' in text:
            return 'CONTRACT'
        elif 'intern' in text:
            return 'INTERNSHIP'
        else:
            return 'FULL_TIME'

    def _extract_description(self, row):
        """Extract job description"""
        desc_elem = row.find('div', class_='description')
        return desc_elem.text.strip() if desc_elem else "No description available"

    def _extract_requirements(self, row):
        """Extract requirements from job description"""
        description = self._extract_description(row)
        
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

    def _extract_date(self, row):
        """Extract and parse posting date"""
        date_elem = row.find('time', datetime=True)
        if date_elem and date_elem.get('datetime'):
            try:
                from datetime import datetime
                date_str = date_elem['datetime']
                return datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
            except Exception:
                pass
        return timezone.now()