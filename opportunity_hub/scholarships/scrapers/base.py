from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.utils import timezone
import time
import logging
import random
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class BaseScholarshipScraper(ABC):
    def __init__(self):
        options = uc.ChromeOptions()
        # Basic options
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Randomize viewport size to appear more human-like
        width = random.randint(1024, 1920)
        height = random.randint(768, 1080)
        options.add_argument(f'--window-size={width},{height}')
        
        # Add random user agent
        ua = UserAgent()
        options.add_argument(f'--user-agent={ua.random}')
        
        # Add additional anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Initialize undetected-chromedriver
        self.driver = uc.Chrome(options=options)
        
        # Add some randomization to appear more human-like
        self.driver.implicitly_wait(random.uniform(8, 12))  # Random wait time between 8-12 seconds

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def wait_for_element(self, by, value, timeout=15):
        """Wait for an element to be present on the page with human-like behavior"""
        try:
            # Add random delay before looking for element
            time.sleep(random.uniform(1, 3))
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            # Simulate human observation time
            time.sleep(random.uniform(0.5, 1.5))
            return element
        except Exception as e:
            logger.error(f"Error waiting for element {value}: {str(e)}")
            logger.error(f"Current URL: {self.driver.current_url}")
            logger.error(f"Page source preview: {self.driver.page_source[:500]}")
            return None

    def scroll_page(self, scroll_pause_time=None):
        """Scroll the page to load dynamic content with human-like behavior"""
        try:
            viewport_height = self.driver.execute_script("return window.innerHeight")
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            
            while current_position < page_height:
                # Random scroll amount between 100 and viewport height
                scroll_amount = random.randint(100, viewport_height)
                current_position += scroll_amount
                
                # Scroll with smooth behavior
                self.driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}})")
                
                # Random pause between scrolls (0.5 to 2.5 seconds)
                time.sleep(random.uniform(0.5, 2.5))
                
                # Occasionally scroll back up a bit (20% chance)
                if random.random() < 0.2:
                    scroll_back = random.randint(50, 200)
                    current_position -= scroll_back
                    self.driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}})")
                    time.sleep(random.uniform(0.3, 1.0))
                
                # Update page height in case of dynamic content
                page_height = self.driver.execute_script("return document.body.scrollHeight")
        except Exception as e:
            logger.error(f"Error scrolling page: {str(e)}")

    def simulate_human_interaction(self):
        """Add random mouse movements and delays to appear more human-like"""
        try:
            # Random mouse movements
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            for _ in range(random.randint(2, 5)):
                if elements:
                    element = random.choice(elements)
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(random.uniform(0.5, 1.5))
                    except:
                        pass
            
            # Random viewport adjustments
            self.driver.execute_script(f"window.scrollTo({{top: {random.randint(100, 500)}, behavior: 'smooth'}})")
            time.sleep(random.uniform(0.3, 1.0))
            
        except Exception as e:
            logger.error(f"Error in human interaction simulation: {str(e)}")

    def _determine_education_level(self, text):
        """Helper method to determine education level from text"""
        text = text.lower()
        if 'phd' in text or 'doctorate' in text:
            return 'PHD'
        elif 'master' in text or 'graduate' in text:
            return 'MASTERS'
        elif 'undergraduate' in text or 'bachelor' in text:
            return 'UNDERGRADUATE'
        elif 'postdoc' in text or 'post-doc' in text:
            return 'POSTDOC'
        else:
            return 'ALL'

    def _parse_date(self, date_string):
        """Helper method to parse various date formats"""
        try:
            from dateutil import parser
            return parser.parse(date_string).date()
        except Exception:
            logger.error(f"Error parsing date: {date_string}")
            return timezone.now().date()

    @abstractmethod
    def scrape_scholarships(self, field_of_study=None, country=None, num_pages=1):
        """
        Abstract method to scrape scholarships from a specific site
        Returns: list of scholarship dictionaries
        """
        pass