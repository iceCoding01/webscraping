from .base import BaseScholarshipScraper
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class InternationalScholarshipsScraper(BaseScholarshipScraper):
    def scrape_scholarships(self, field_of_study=None, country=None, num_pages=1):
        """
        Scrape scholarships from InternationalScholarships.com
        """
        scholarships = []
        
        try:
            # Start with the main scholarships page
            base_url = 'https://www.internationalscholarships.com/search'
            if field_of_study:
                base_url += f'?field={field_of_study}'
            if country:
                base_url += f'{"?" if "?" not in base_url else "&"}country={country}'

            # Process multiple pages
            for page in range(num_pages):
                url = f"{base_url}&page={page+1}" if "?" in base_url else f"{base_url}?page={page+1}"
                self.driver.get(url)
                
                # Wait for scholarship listings
                self.wait_for_element(By.CLASS_NAME, 'scholarship-item')
                self.scroll_page()

                # Parse page content
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                scholarship_items = soup.find_all('div', class_='scholarship-item')

                for item in scholarship_items:
                    try:
                        title_elem = item.find('h2', class_='title') or item.find('h3', class_='title')
                        desc_elem = item.find('div', class_='description')
                        amount_elem = item.find('div', class_='award')
                        deadline_elem = item.find('div', class_='deadline')
                        
                        scholarship = {
                            'title': title_elem.text.strip() if title_elem else 'Untitled Scholarship',
                            'organization': self._get_organization(item),
                            'description': desc_elem.text.strip() if desc_elem else 'No description available',
                            'requirements': self._get_requirements(item),
                            'amount': amount_elem.text.strip() if amount_elem else 'Amount not specified',
                            'country': country or self._get_country(item) or 'International',
                            'education_level': self._get_education_level(item),
                            'field_of_study': field_of_study or self._get_field(item),
                            'deadline': self._parse_date(deadline_elem.text) if deadline_elem else None,
                            'website_url': self._get_website_url(item),
                            'source_website': 'InternationalScholarships.com',
                            'is_fully_funded': self._is_fully_funded(item),
                            'is_active': True
                        }
                        scholarships.append(scholarship)

                    except Exception as e:
                        logger.error(f"Error extracting scholarship data: {str(e)}")
                        continue

        except Exception as e:
            logger.error(f"Error scraping InternationalScholarships.com: {str(e)}")

        return scholarships

    def _get_organization(self, item):
        """Extract organization from scholarship item"""
        org_elem = item.find('div', class_='provider') or item.find('div', class_='organization')
        return org_elem.text.strip() if org_elem else 'Unknown Organization'

    def _get_requirements(self, item):
        """Extract requirements from scholarship item"""
        req_elem = item.find('div', class_='requirements') or item.find('div', class_='eligibility')
        if not req_elem:
            return "No requirements specified"
        
        requirements = []
        for req in req_elem.find_all(['li', 'p']):
            requirements.append(req.text.strip())
        
        return '\n'.join(requirements) if requirements else req_elem.text.strip()

    def _get_country(self, item):
        """Extract country information"""
        country_elem = item.find('div', class_='country') or item.find('div', class_='location')
        return country_elem.text.strip() if country_elem else None

    def _get_field(self, item):
        """Extract field of study"""
        field_elem = item.find('div', class_='field') or item.find('div', class_='study-field')
        return field_elem.text.strip() if field_elem else 'All Fields'

    def _get_website_url(self, item):
        """Extract scholarship URL"""
        link = item.find('a', class_='scholarship-link') or item.find('a', class_='title')
        if link and link.get('href'):
            href = link['href']
            return href if href.startswith('http') else f"https://www.internationalscholarships.com{href}"
        return None

    def _is_fully_funded(self, item):
        """Check if scholarship is fully funded"""
        text = item.get_text().lower()
        return any(term in text for term in ['full scholarship', 'fully funded', 'full funding', 'full tuition'])