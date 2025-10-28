from .base import BaseScholarshipScraper
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class CheetahScraper(BaseScholarshipScraper):
    def scrape_scholarships(self, field_of_study=None, country=None, num_pages=1):
        """
        Scrape scholarships from Cheetah (formerly International Scholarships)
        """
        scholarships = []
        
        try:
            for page in range(num_pages):
                url = f'https://www.cheetah.org/scholarships/page/{page+1}/'
                if field_of_study:
                    url += f'?study={field_of_study}'
                if country:
                    url += f'&country={country}'
                
                self.driver.get(url)
                self.wait_for_element(By.CLASS_NAME, 'scholarship-item')
                self.scroll_page()
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                scholarship_items = soup.find_all('div', class_='scholarship-item')
                
                for item in scholarship_items:
                    try:
                        scholarship = {
                            'title': self._get_title(item),
                            'organization': self._get_organization(item),
                            'description': self._get_description(item),
                            'requirements': self._get_requirements(item),
                            'amount': self._get_amount(item),
                            'country': country or self._get_country(item) or 'International',
                            'education_level': self._get_education_level(item),
                            'field_of_study': field_of_study or self._get_field_of_study(item),
                            'deadline': self._get_deadline(item),
                            'website_url': self._get_website_url(item),
                            'source_website': 'Cheetah.org',
                            'is_fully_funded': self._is_fully_funded(item),
                            'is_active': True
                        }
                        scholarships.append(scholarship)
                        
                    except Exception as e:
                        logger.error(f"Error extracting Cheetah scholarship data: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error scraping Cheetah: {str(e)}")
        
        return scholarships

    def _get_title(self, item):
        """Extract scholarship title"""
        title_elem = item.find('h2', class_='scholarship-title')
        return title_elem.text.strip() if title_elem else 'Untitled Scholarship'

    def _get_organization(self, item):
        """Extract organization name"""
        org_elem = item.find('div', class_='scholarship-provider')
        return org_elem.text.strip() if org_elem else 'Unknown Organization'

    def _get_description(self, item):
        """Extract scholarship description"""
        desc_elem = item.find('div', class_='scholarship-description')
        return desc_elem.text.strip() if desc_elem else 'No description available'

    def _get_requirements(self, item):
        """Extract scholarship requirements"""
        req_elem = item.find('div', class_='scholarship-requirements')
        if not req_elem:
            return "No requirements specified"
            
        requirements = []
        for req in req_elem.find_all('li'):
            requirements.append(req.text.strip())
            
        return '\n'.join(requirements) if requirements else req_elem.text.strip()

    def _get_amount(self, item):
        """Extract scholarship amount"""
        amount_elem = item.find('div', class_='scholarship-amount')
        return amount_elem.text.strip() if amount_elem else 'Amount not specified'

    def _get_country(self, item):
        """Extract scholarship country"""
        country_elem = item.find('div', class_='scholarship-country')
        return country_elem.text.strip() if country_elem else None

    def _get_education_level(self, item):
        """Extract education level"""
        level_elem = item.find('div', class_='scholarship-level')
        return level_elem.text.strip() if level_elem else 'Not specified'

    def _get_field_of_study(self, item):
        """Extract field of study"""
        field_elem = item.find('div', class_='scholarship-field')
        return field_elem.text.strip() if field_elem else 'All Fields'

    def _get_deadline(self, item):
        """Extract and parse deadline date"""
        deadline_elem = item.find('div', class_='scholarship-deadline')
        if deadline_elem:
            return self._parse_date(deadline_elem.text.strip())
        return None

    def _get_website_url(self, item):
        """Extract scholarship URL"""
        link = item.find('a', class_='scholarship-link')
        return link['href'] if link else None

    def _is_fully_funded(self, item):
        """Determine if scholarship is fully funded"""
        amount = self._get_amount(item).lower()
        return any(term in amount for term in ['full', 'complete', '100%'])