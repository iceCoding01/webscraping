from .base import BaseScholarshipScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import logging
import time
import random

logger = logging.getLogger(__name__)

class ScholarshipsPositionsPortalScraper(BaseScholarshipScraper):
    """
    Scraper for ScholarshipsPositionsPortal.com - a site that explicitly allows reasonable scraping
    through their robots.txt
    """
    def scrape_scholarships(self, field_of_study=None, country=None, num_pages=1):
        """
        Scrape scholarships from ScholarshipsPositionsPortal
        """
        scholarships = []
        
        try:
            # Base URL for scholarship search
            base_url = 'https://scholarship-positions.com'
            
            for page in range(num_pages):
                try:
                    # Construct URL with filters
                    url = f"{base_url}/category/international-scholarships/"
                    if page > 0:
                        url += f"page/{page + 1}/"
                    
                    logger.info(f"Accessing page {page + 1}: {url}")
                    self.driver.get(url)
                    
                    # Add random delay to respect the site
                    time.sleep(random.uniform(2, 4))
                    
                    # Wait for scholarship listings
                    self.wait_for_element(By.CLASS_NAME, 'post')
                    
                    # Scroll slowly to simulate human behavior
                    self.scroll_page()
                    
                    # Parse the page
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    scholarship_posts = soup.find_all('article', class_='post')
                    
                    for post in scholarship_posts:
                        try:
                            # Extract scholarship details
                            title_elem = post.find('h2', class_='entry-title')
                            content_elem = post.find('div', class_='entry-content')
                            meta_elem = post.find('div', class_='entry-meta')
                            
                            if not title_elem or not content_elem:
                                continue
                                
                            # Extract details from content
                            content_text = content_elem.get_text()
                            scholarship = {
                                'title': title_elem.text.strip(),
                                'organization': self._extract_organization(content_text),
                                'description': self._clean_description(content_text),
                                'requirements': self._extract_requirements(content_text),
                                'amount': self._extract_amount(content_text),
                                'country': country or self._extract_country(content_text),
                                'education_level': self._determine_education_level(content_text),
                                'field_of_study': field_of_study or self._extract_field(content_text),
                                'deadline': self._extract_deadline(content_text),
                                'website_url': title_elem.find('a')['href'] if title_elem.find('a') else None,
                                'source_website': 'Scholarship-Positions.com',
                                'is_fully_funded': self._is_fully_funded(content_text),
                                'is_active': True
                            }
                            
                            # Only add if we have essential details
                            if scholarship['title'] and scholarship['description']:
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
            logger.error(f"Error in ScholarshipsPositionsPortal scraper: {str(e)}")
            
        return scholarships
        
    def _clean_description(self, text):
        """Clean and format the description text"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        # Limit length
        return text[:500] + '...' if len(text) > 500 else text
        
    def _extract_organization(self, text):
        """Extract organization name from content"""
        keywords = ['offered by', 'provided by', 'sponsored by']
        for keyword in keywords:
            if keyword in text.lower():
                start = text.lower().index(keyword) + len(keyword)
                end = text.find('.', start)
                if end != -1:
                    return text[start:end].strip()
        return 'Unknown Organization'
        
    def _extract_requirements(self, text):
        """Extract requirements from content"""
        keywords = ['requirements:', 'eligible:', 'eligibility:', 'criteria:']
        requirements = []
        
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                start = text_lower.index(keyword) + len(keyword)
                end = text.find('\n', start)
                if end == -1:
                    end = text.find('. ', start)
                if end != -1:
                    requirements.append(text[start:end].strip())
                    
        return '\n'.join(requirements) if requirements else "Requirements not specified"
        
    def _extract_amount(self, text):
        """Extract scholarship amount from content"""
        amount_indicators = ['$', '€', '£', 'USD', 'EUR', 'GBP']
        text_lower = text.lower()
        
        for indicator in amount_indicators:
            if indicator in text:
                # Find the sentence containing the amount
                start = text.find(indicator)
                end = text.find('.', start)
                if end != -1:
                    amount_text = text[start:end].strip()
                    return amount_text
                    
        # Check for full funding mentions
        if any(term in text_lower for term in ['full scholarship', 'fully funded']):
            return "Fully Funded"
            
        return "Amount not specified"
        
    def _extract_deadline(self, text):
        """Extract application deadline from content"""
        deadline_indicators = ['deadline:', 'due date:', 'closes on:', 'apply by:']
        text_lower = text.lower()
        
        for indicator in deadline_indicators:
            if indicator in text_lower:
                start = text_lower.index(indicator) + len(indicator)
                end = text.find('.', start)
                if end != -1:
                    date_text = text[start:end].strip()
                    try:
                        return self._parse_date(date_text)
                    except:
                        continue
                        
        return None
        
    def _extract_country(self, text):
        """Extract country from content"""
        text_lower = text.lower()
        if 'in ' in text_lower and ' university' in text_lower:
            start = text_lower.index('in ') + 3
            end = text_lower.find(' university', start)
            if end != -1:
                return text[start:end].strip()
        return None
        
    def _extract_field(self, text):
        """Extract field of study from content"""
        field_indicators = ['field of study:', 'subject area:', 'discipline:']
        text_lower = text.lower()
        
        for indicator in field_indicators:
            if indicator in text_lower:
                start = text_lower.index(indicator) + len(indicator)
                end = text.find('.', start)
                if end != -1:
                    return text[start:end].strip()
                    
        return 'All Fields'
        
    def _is_fully_funded(self, text):
        """Check if scholarship is fully funded"""
        text_lower = text.lower()
        fully_funded_terms = [
            'full scholarship',
            'fully funded',
            'full funding',
            'complete funding',
            'full tuition'
        ]
        return any(term in text_lower for term in fully_funded_terms)