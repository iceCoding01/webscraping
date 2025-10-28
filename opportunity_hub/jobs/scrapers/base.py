from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.utils import timezone
import time
import logging

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present on the page"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            logger.error(f"Error waiting for element {value}: {str(e)}")
            return None

    def scroll_page(self, scroll_pause_time=1.0):
        """Scroll the page to load dynamic content"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            logger.error(f"Error scrolling page: {str(e)}")

    @abstractmethod
    def scrape_jobs(self, keywords=None, location=None, num_pages=1):
        """
        Abstract method to scrape jobs from a specific site
        Returns: list of job dictionaries
        """
        pass