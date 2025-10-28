from .base import BaseScholarshipScraper
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class FastWebScraper(BaseScholarshipScraper):
    def scrape_scholarships(self, field_of_study=None, country=None, num_pages=1):
        """
        Scrape scholarships from FastWeb
        """
        scholarships = []
        
        try:
            for page in range(num_pages):
                url = 'https://www.fastweb.com/college-scholarships'
                if page > 0:
                    url += f'?page={page+1}'
                if field_of_study:
                    url += '&field=' + field_of_study.lower().replace(' ', '-')
                
                self.driver.get(url)
                self.wait_for_element(By.CLASS_NAME, 'scholarship-result')
                self.scroll_page()
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                scholarship_results = soup.find_all('div', class_='scholarship-result')
                
                for result in scholarship_results:
                    try:
                        scholarship = {
                            'title': self._extract_title(result),
                            'organization': self._extract_provider(result),
                            'description': self._extract_description(result),
                            'requirements': self._extract_requirements(result),
                            'amount': self._extract_amount(result),
                            'country': country or 'United States',  # FastWeb primarily focuses on US scholarships
                            'education_level': self._extract_education_level(result),
                            'field_of_study': field_of_study or self._extract_field_of_study(result),
                            'deadline': self._extract_deadline(result),
                            'website_url': self._extract_url(result),
                            'source_website': 'FastWeb.com',
                            'is_fully_funded': self._check_fully_funded(result),
                            'is_active': True
                        }
                        scholarships.append(scholarship)
                        
                    except Exception as e:
                        logger.error(f"Error extracting FastWeb scholarship data: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error scraping FastWeb: {str(e)}")
        
        return scholarships

    def _extract_title(self, result):
        """Extract scholarship title"""
        title_elem = result.find('h3', class_='scholarship-title')
        return title_elem.text.strip() if title_elem else 'Untitled Scholarship'

    def _extract_provider(self, result):
        """Extract scholarship provider"""
        provider_elem = result.find('div', class_='provider')
        return provider_elem.text.strip() if provider_elem else 'Unknown Provider'

    def _extract_description(self, result):
        """Extract scholarship description"""
        desc_elem = result.find('div', class_='description')
        return desc_elem.text.strip() if desc_elem else 'No description available'

    def _extract_requirements(self, result):
        """Extract scholarship requirements"""
        req_elem = result.find('div', class_='requirements')
        if not req_elem:
            return "No requirements specified"
            
        requirements = []
        for req in req_elem.find_all('li'):
            requirements.append(req.text.strip())
            
        return '\n'.join(requirements) if requirements else req_elem.text.strip()

    def _extract_amount(self, result):
        """Extract scholarship amount"""
        amount_elem = result.find('div', class_='award-amount')
        return amount_elem.text.strip() if amount_elem else 'Amount not specified'

    def _extract_education_level(self, result):
        """Extract education level requirements"""
        level_elem = result.find('div', class_='education-level')
        return level_elem.text.strip() if level_elem else 'Not specified'

    def _extract_field_of_study(self, result):
        """Extract field of study"""
        field_elem = result.find('div', class_='field-of-study')
        return field_elem.text.strip() if field_elem else 'All Fields'

    def _extract_deadline(self, result):
        """Extract and parse deadline date"""
        deadline_elem = result.find('div', class_='deadline')
        if deadline_elem:
            return self._parse_date(deadline_elem.text.strip())
        return None

    def _extract_url(self, result):
        """Extract scholarship URL"""
        link = result.find('a', class_='scholarship-link')
        return 'https://www.fastweb.com' + link['href'] if link else None

    def _check_fully_funded(self, result):
        """Check if scholarship is fully funded"""
        amount = self._extract_amount(result).lower()
        return any(term in amount for term in ['full tuition', 'full ride', '100% coverage'])