import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from django.utils import timezone

class ScholarshipScraper:
    def __init__(self):
        # Set up headless Chrome browser for Selenium
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape_scholarships_com(self):
        """Scrape scholarships from Scholarships.com"""
        scholarships = []
        url = 'https://www.scholarships.com/financial-aid/college-scholarships/scholarship-directory'
        
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        scholarship_cards = soup.find_all('div', class_='scholarship-listing')
        
        for card in scholarship_cards:
            try:
                scholarship = {
                    'title': card.find('h3', class_='scholarship-title').text.strip(),
                    'organization': card.find('div', class_='scholarship-sponsor').text.strip(),
                    'amount': card.find('div', class_='scholarship-amount').text.strip(),
                    'deadline': self._parse_date(card.find('div', class_='scholarship-deadline').text.strip()),
                    'description': card.find('div', class_='scholarship-description').text.strip(),
                    'website_url': card.find('a', class_='scholarship-details')['href'],
                    'source_website': 'Scholarships.com'
                }
                scholarships.append(scholarship)
            except Exception as e:
                print(f"Error scraping Scholarships.com: {e}")
                
        return scholarships

    def scrape_fulbright(self):
        """Scrape Fulbright scholarships"""
        scholarships = []
        url = 'https://foreign.fulbrightonline.org/applicants/getting-started'
        
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        scholarship_sections = soup.find_all('div', class_='scholarship-opportunity')
        
        for section in scholarship_sections:
            try:
                scholarship = {
                    'title': 'Fulbright Scholarship',
                    'organization': 'Fulbright',
                    'description': section.find('div', class_='description').text.strip(),
                    'country': section.find('div', class_='country').text.strip(),
                    'deadline': self._parse_date(section.find('div', class_='deadline').text.strip()),
                    'website_url': url,
                    'source_website': 'Fulbright',
                    'is_fully_funded': True,
                    'education_level': 'GRADUATE'
                }
                scholarships.append(scholarship)
            except Exception as e:
                print(f"Error scraping Fulbright: {e}")
                
        return scholarships

    def scrape_erasmus(self):
        """Scrape Erasmus Mundus scholarships"""
        scholarships = []
        url = 'https://erasmus-plus.ec.europa.eu/opportunities/opportunities-for-individuals/students/erasmus-mundus-joint-masters-scholarships'
        
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        programs = soup.find_all('div', class_='programme-card')
        
        for program in programs:
            try:
                scholarship = {
                    'title': 'Erasmus Mundus Scholarship - ' + program.find('h3').text.strip(),
                    'organization': 'European Commission',
                    'description': program.find('div', class_='description').text.strip(),
                    'country': 'European Union',
                    'deadline': self._parse_date(program.find('div', class_='deadline').text.strip()),
                    'website_url': url,
                    'source_website': 'Erasmus',
                    'is_fully_funded': True,
                    'education_level': 'MASTERS'
                }
                scholarships.append(scholarship)
            except Exception as e:
                print(f"Error scraping Erasmus: {e}")
                
        return scholarships

    def _parse_date(self, date_string):
        """Helper method to parse dates from various formats"""
        try:
            # Add your date parsing logic here
            # This is a simplified example
            return datetime.strptime(date_string, '%m/%d/%Y').date()
        except:
            return timezone.now().date()

    def __del__(self):
        """Close the browser when done"""
        self.driver.quit()