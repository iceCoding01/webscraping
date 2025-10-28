from .base import BaseScholarshipScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging
import time
import random

logger = logging.getLogger(__name__)

class UniversityPositionsScraper(BaseScholarshipScraper):
    """
    Scraper for UniversityPositions.eu - a site that explicitly allows reasonable scraping
    and provides structured scholarship data
    """
    def scrape_scholarships(self, field_of_study=None, country=None, num_pages=1):
        """
        Scrape scholarships from UniversityPositions.eu
        """
        scholarships = []
        
        try:
            # Base URL for scholarship search
            base_url = 'https://www.universitypositions.eu/scholarships'
            
            for page in range(num_pages):
                try:
                    # Construct URL with filters
                    url = base_url
                    filters = []
                    if field_of_study:
                        filters.append(f"field={field_of_study}")
                    if country:
                        filters.append(f"country={country}")
                    if page > 0:
                        filters.append(f"page={page + 1}")
                    if filters:
                        url += '?' + '&'.join(filters)
                    
                    logger.info(f"Accessing page {page + 1}: {url}")
                    self.driver.get(url)
                    
                    # Add random delay to respect the site
                    time.sleep(random.uniform(2, 4))
                    
                    # Wait for scholarship listings
                    self.wait_for_element(By.CLASS_NAME, 'scholarship-item')
                    
                    # Scroll slowly to simulate human behavior
                    self.scroll_page()
                    
                    # Parse the page
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    scholarship_items = soup.find_all('div', class_='scholarship-item')
                    
                    for item in scholarship_items:
                        try:
                            # Extract scholarship details from structured data
                            title_elem = item.find('h3', class_='title')
                            org_elem = item.find('div', class_='organization')
                            details_elem = item.find('div', class_='details')
                            
                            if not title_elem:
                                continue
                                
                            scholarship = {
                                'title': title_elem.text.strip(),
                                'organization': org_elem.text.strip() if org_elem else 'Unknown Organization',
                                'description': self._extract_description(item),
                                'requirements': self._extract_requirements(item),
                                'amount': self._extract_amount(item),
                                'country': country or self._extract_country(item),
                                'education_level': self._extract_education_level(item),
                                'field_of_study': field_of_study or self._extract_field(item),
                                'deadline': self._extract_deadline(item),
                                'website_url': self._extract_url(item),
                                'source_website': 'UniversityPositions.eu',
                                'is_fully_funded': self._is_fully_funded(item),
                                'is_active': True
                            }
                            
                            scholarships.append(scholarship)
                            
                        except Exception as e:
                            logger.error(f"Error extracting scholarship details: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error processing page {page + 1}: {str(e)}")
                    continue
                    
                # Respect the site's rate limits
                time.sleep(random.uniform(3, 5))
                
        except Exception as e:
            logger.error(f"Error in UniversityPositions scraper: {str(e)}")
            
        return scholarships
        
    def _extract_description(self, item):
        """Extract scholarship description"""
        desc_elem = item.find('div', class_='description')
        if desc_elem:
            text = desc_elem.text.strip()
            # Limit description length
            return text[:500] + '...' if len(text) > 500 else text
        return "No description available"
        
    def _extract_requirements(self, item):
        """Extract scholarship requirements"""
        req_elem = item.find('div', class_='requirements')
        if not req_elem:
            return "Requirements not specified"
            
        requirements = []
        for req in req_elem.find_all('li'):
            requirements.append(req.text.strip())
            
        return '\n'.join(requirements) if requirements else req_elem.text.strip()
        
    def _extract_amount(self, item):
        """Extract scholarship amount"""
        amount_elem = item.find('div', class_='funding')
        return amount_elem.text.strip() if amount_elem else "Amount not specified"
        
    def _extract_country(self, item):
        """Extract country information"""
        country_elem = item.find('div', class_='location')
        return country_elem.text.strip() if country_elem else None
        
    def _extract_education_level(self, item):
        """Extract education level"""
        level_elem = item.find('div', class_='degree-level')
        if level_elem:
            return self._determine_education_level(level_elem.text)
        return 'ALL'
        
    def _extract_field(self, item):
        """Extract field of study"""
        field_elem = item.find('div', class_='field')
        return field_elem.text.strip() if field_elem else 'All Fields'
        
    def _extract_deadline(self, item):
        """Extract application deadline"""
        deadline_elem = item.find('div', class_='deadline')
        if deadline_elem:
            try:
                return self._parse_date(deadline_elem.text.strip())
            except:
                return None
        return None
        
    def _extract_url(self, item):
        """Extract scholarship URL"""
        link = item.find('a', class_='apply-link')
        return link['href'] if link and 'href' in link.attrs else None
        
    def _is_fully_funded(self, item):
        """Check if scholarship is fully funded"""
        text = item.get_text().lower()
        funding_elem = item.find('div', class_='funding')
        if funding_elem:
            text += ' ' + funding_elem.text.lower()
            
        fully_funded_terms = [
            'full scholarship',
            'fully funded',
            'full funding',
            'complete funding',
            'full tuition'
        ]
        return any(term in text for term in fully_funded_terms)