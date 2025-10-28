from .base import BaseScholarshipScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from django.utils import timezone
import logging
import time
import random

logger = logging.getLogger(__name__)

class ScholarshipsDotComScraper(BaseScholarshipScraper):
    def scrape_scholarships(self, field_of_study=None, country=None, num_pages=1):
        """
        Scrape scholarships from Scholarships.com with enhanced bot detection avoidance
        """
        scholarships = []
        field_of_study = field_of_study or "all-fields"
        max_retries = 3
        
        try:
            # Start with the homepage to establish a normal browsing pattern
            logger.info("Accessing homepage first...")
            self.driver.get('https://www.scholarships.com')
            time.sleep(random.uniform(3, 5))
            
            # Check for CAPTCHA or blocking
            if self._is_blocked():
                logger.error("Initial access blocked - possible CAPTCHA or IP ban")
                return []
            
            # Simulate human browsing pattern
            self.simulate_human_interaction()
            
            # Now proceed with scholarship search
            for page in range(num_pages):
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        url = 'https://www.scholarships.com/financial-aid/college-scholarships/scholarship-directory'
                        if field_of_study:
                            url += f'/field-of-study/{field_of_study}'
                        if country:
                            url += f'/country/{country}'
                        if page > 0:
                            url += f'?page={page+1}'
                        
                        logger.info(f"Accessing page {page + 1}...")
                        self.driver.get(url)
                        
                        # Random delay before interactions
                        time.sleep(random.uniform(2, 4))
                        
                        if self._is_blocked():
                            logger.warning(f"Blocked on attempt {retry_count + 1} - waiting before retry")
                            time.sleep(random.uniform(30, 60))  # Longer wait between retries
                            retry_count += 1
                            continue
                        
                        # Wait for content with increased timeout
                        element = self.wait_for_element(By.CLASS_NAME, 'scholarship-listing', timeout=20)
                        if not element:
                            logger.warning(f"No scholarships found on attempt {retry_count + 1}")
                            retry_count += 1
                            continue
                            
                        # Simulate human reading behavior
                        self.simulate_human_interaction()
                        self.scroll_page()
                        break  # Success - exit retry loop
                        
                    except Exception as e:
                        logger.error(f"Error on attempt {retry_count + 1}: {str(e)}")
                        if retry_count < max_retries - 1:
                            retry_count += 1
                            time.sleep(random.uniform(20, 40))
                            continue
                        raise  # Re-raise the last exception if all retries failed
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                scholarship_cards = soup.find_all('div', class_='scholarship-listing')
                
                for card in scholarship_cards:
                    try:
                        title_elem = card.find('h3', class_='scholarship-title')
                        org_elem = card.find('div', class_='scholarship-sponsor')
                        amount_elem = card.find('div', class_='scholarship-amount')
                        deadline_elem = card.find('div', class_='scholarship-deadline')
                        
                        scholarship = {
                            'title': title_elem.text.strip() if title_elem else 'Untitled Scholarship',
                            'organization': org_elem.text.strip() if org_elem else 'Unknown Organization',
                            'description': self._extract_description(card),
                            'requirements': self._extract_requirements(card),
                            'amount': amount_elem.text.strip() if amount_elem else 'Amount not specified',
                            'country': country or 'International',
                            'education_level': self._determine_education_level(
                                card.find('div', class_='scholarship-details').text
                            ),
                            'field_of_study': field_of_study.replace('-', ' ').title(),
                            'deadline': self._parse_date(deadline_elem.text.strip()) if deadline_elem else None,
                            'website_url': self._get_website_url(card),
                            'source_website': 'Scholarships.com',
                            'is_fully_funded': 'full' in (amount_elem.text.lower() if amount_elem else ''),
                            'is_active': True
                        }
                        scholarships.append(scholarship)
                        
                    except Exception as e:
                        logger.error(f"Error extracting Scholarships.com data: {str(e)}")
                        continue

        except Exception as e:
            logger.error(f"Error scraping Scholarships.com: {str(e)}")
        
        return scholarships

    def _extract_description(self, card):
        """Extract scholarship description"""
        desc_elem = card.find('div', class_='scholarship-description')
        return desc_elem.text.strip() if desc_elem else "No description available"

    def _extract_requirements(self, card):
        """Extract scholarship requirements"""
        details = card.find('div', class_='scholarship-details')
        if not details:
            return "No requirements specified"
        
        requirements = []
        for item in details.find_all('li'):
            requirements.append(item.text.strip())
            
        return '\n'.join(requirements) if requirements else details.text.strip()

    def _get_website_url(self, card):
        """Get the scholarship website URL"""
        link = card.find('a', class_='scholarship-title-link')
        return 'https://www.scholarships.com' + link['href'] if link else None
        
    def _is_blocked(self):
        """Check if we're being blocked or presented with a CAPTCHA"""
        page_source = self.driver.page_source.lower()
        page_title = self.driver.title.lower()
        current_url = self.driver.current_url.lower()
        
        # Common blocking indicators
        block_indicators = [
            'captcha',
            'security check',
            'please verify you are a human',
            'access denied',
            'blocked',
            'suspicious activity',
            'unusual traffic',
            'cloudflare',
            'ddos protection',
            'please wait',
            'just a moment',
            'checking your browser'
        ]
        
        # Check page content for blocking indicators
        for indicator in block_indicators:
            if indicator in page_source or indicator in page_title:
                logger.warning(f"Detected blocking indicator: {indicator}")
                return True
        
        # Check for redirect to security pages
        security_urls = ['security', 'verify', 'check', 'captcha', 'challenge']
        if any(term in current_url for term in security_urls):
            logger.warning(f"Redirected to security page: {current_url}")
            return True
        
        # Check if expected content is missing
        if 'scholarship' not in page_source:
            logger.warning("Expected content missing from page")
            return True
            
        return False