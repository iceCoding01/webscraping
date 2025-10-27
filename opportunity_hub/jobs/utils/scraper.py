import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from django.utils import timezone

class JobScraper:
    def __init__(self):
        # Set up headless Chrome browser for Selenium
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def scrape_indeed(self, query='python developer', location='remote'):
        """Scrape job listings from Indeed"""
        jobs = []
        url = f'https://www.indeed.com/jobs?q={query}&l={location}'
        
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        for card in job_cards:
            try:
                job = {
                    'title': card.find('h2', class_='jobTitle').text.strip(),
                    'company': card.find('span', class_='companyName').text.strip(),
                    'location': card.find('div', class_='companyLocation').text.strip(),
                    'description': card.find('div', class_='job-snippet').text.strip(),
                    'posted_date': timezone.now(),
                    'source_website': 'Indeed',
                    'application_url': 'https://indeed.com' + card.find('a')['href']
                }
                jobs.append(job)
            except Exception as e:
                print(f"Error scraping Indeed job: {e}")
                
        return jobs

    def scrape_linkedin(self, query='python developer'):
        """Scrape job listings from LinkedIn"""
        jobs = []
        url = f'https://www.linkedin.com/jobs/search?keywords={query}'
        
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        job_cards = soup.find_all('div', class_='base-search-card')
        
        for card in job_cards:
            try:
                job = {
                    'title': card.find('h3', class_='base-search-card__title').text.strip(),
                    'company': card.find('h4', class_='base-search-card__subtitle').text.strip(),
                    'location': card.find('span', class_='job-search-card__location').text.strip(),
                    'description': card.find('p', class_='base-search-card__metadata').text.strip(),
                    'posted_date': timezone.now(),
                    'source_website': 'LinkedIn',
                    'application_url': card.find('a', class_='base-card__full-link')['href']
                }
                jobs.append(job)
            except Exception as e:
                print(f"Error scraping LinkedIn job: {e}")
                
        return jobs

    def scrape_remoteok(self):
        """Scrape job listings from RemoteOK"""
        jobs = []
        url = 'https://remoteok.com/remote-dev-jobs'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        job_cards = soup.find_all('tr', class_='job')
        
        for card in job_cards:
            try:
                job = {
                    'title': card.find('h2', itemprop='title').text.strip(),
                    'company': card.find('h3', itemprop='name').text.strip(),
                    'description': card.find('div', class_='description').text.strip(),
                    'posted_date': timezone.now(),
                    'source_website': 'RemoteOK',
                    'application_url': 'https://remoteok.com' + card.find('a', class_='preventLink')['href'],
                    'is_remote': True
                }
                jobs.append(job)
            except Exception as e:
                print(f"Error scraping RemoteOK job: {e}")
                
        return jobs

    def __del__(self):
        """Close the browser when done"""
        self.driver.quit()