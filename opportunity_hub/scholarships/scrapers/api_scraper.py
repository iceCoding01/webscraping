import requests
from datetime import datetime
import logging
from bs4 import BeautifulSoup, Tag
from django.utils import timezone
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class APIScholarshipScraper:
    """
    Scraper that uses official APIs and RSS feeds to collect scholarship data
    """
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OpportunityHub/1.0 (Academic Project; contact@opportunityhub.edu)'
        })

    def scrape_scholarships(self, field_of_study=None, country=None, num_pages=1) -> List[Dict[str, Any]]:
        """
        Collect scholarships from multiple sources
        """
        scholarships = []
        
        # Get DAAD scholarships
        daad_scholarships = self._get_daad_scholarships(field_of_study, country)
        scholarships.extend(daad_scholarships)
        logger.info(f'Found {len(daad_scholarships)} DAAD scholarships')
        
        # Get Swedish Institute scholarships
        si_scholarships = self._get_sweden_scholarships()
        scholarships.extend(si_scholarships)
        logger.info(f'Found {len(si_scholarships)} Swedish Institute scholarships')
        
        # DAAD Scholarships
        try:
            url = "https://www2.daad.de/deutschland/stipendium/datenbank/en/21148-scholarship-database/"
            response = self.session.get(url)
            logger.info(f"DAAD response status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # First, let's log all available div classes to see what we're working with
                div_classes = set()
                for div in soup.find_all('div', class_=True):
                    div_classes.update(div['class'])
                logger.info(f"Available div classes: {div_classes}")
                
                # Try to find any scholarship-related content
                scholarship_elements = soup.find_all(['div', 'article'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['scholarship', 'result', 'listing', 'program']))
                logger.info(f"Found {len(scholarship_elements)} potential scholarship elements")
                
                for item in scholarship_elements:
                    # Try to find title in various ways
                    title = (
                        item.find(['h1', 'h2', 'h3', 'h4'], class_=lambda x: x and 'title' in x.lower() if x else True) or
                        item.find(['a'], class_=lambda x: x and 'title' in x.lower() if x else True)
                    )
                    
                    desc = item.find(['div', 'p'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['desc', 'content', 'text']) if x else True)
                    
                    if title:
                        scholarship = {
                            'title': title.text.strip(),
                            'organization': 'DAAD',
                            'description': desc.text.strip() if desc else '',
                            'requirements': '',
                            'amount': 'See website for details',
                            'country': 'Germany',
                            'education_level': 'ALL',
                            'field_of_study': field_of_study or 'All Fields',
                            'deadline': None,
                            'website_url': 'https://www2.daad.de' + title.get('href') if title.get('href') else '',
                            'source_website': 'DAAD',
                            'is_fully_funded': False,
                            'is_active': True
                        }
                        scholarships.append(scholarship)
                        logger.info(f'Found DAAD scholarship: {scholarship["title"]}')
        except Exception as e:
            logger.error(f"Error fetching DAAD scholarships: {str(e)}", exc_info=True)

        # Erasmus Mundus Joint Masters
        try:
            url = "https://erasmus-plus.ec.europa.eu/opportunities/opportunities-for-individuals/students/erasmus-mundus-joint-masters-scholarships"
            response = self.session.get(url)
            logger.info(f"Erasmus response status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                div_classes = set()
                for div in soup.find_all('div', class_=True):
                    div_classes.update(div['class'])
                logger.info(f"Available Erasmus div classes: {div_classes}")
                
                # Look for programme/course listings
                program_elements = soup.find_all(['div', 'article'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['programme', 'course', 'emjm', 'masters']))
                logger.info(f"Found {len(program_elements)} potential Erasmus programs")
                
                for item in program_elements:
                    title = (
                        item.find(['h1', 'h2', 'h3', 'h4'], recursive=False) or
                        item.find('a', href=True)
                    )
                    desc = item.find(['div', 'p'], class_=lambda x: x and 'description' in x.lower() if x else True)
                    
                    if title:
                        scholarship = {
                            'title': title.text.strip(),
                            'organization': 'European Commission',
                            'description': desc.text.strip() if desc else 'Erasmus Mundus Joint Masters Scholarship',
                            'requirements': 'Bachelor\'s degree required',
                            'amount': 'Full scholarship (1400 EUR/month + other benefits)',
                            'country': 'European Union',
                            'education_level': 'MASTERS',
                            'field_of_study': field_of_study or 'All Fields',
                            'deadline': None,
                            'website_url': title.get('href') if title.get('href') else 'https://erasmus-plus.ec.europa.eu',
                            'source_website': 'Erasmus+',
                            'is_fully_funded': True,
                            'is_active': True
                        }
                        scholarships.append(scholarship)
                        logger.info(f'Found Erasmus scholarship: {scholarship["title"]}')
        except Exception as e:
            logger.error(f"Error fetching Erasmus scholarships: {str(e)}", exc_info=True)

        # Commonwealth Scholarships
        try:
            url = "https://cscuk.fcdo.gov.uk/scholarships/"
            response = self.session.get(url)
            logger.info(f"Commonwealth response status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for scholarship listings
                scholarship_items = soup.find_all('article') or soup.find_all(['div', 'section'], class_=lambda x: x and any(keyword in str(x).lower() for keyword in ['scholarship', 'fellowship']))
                
                for item in scholarship_items:
                    title_elem = item.find(['h1', 'h2', 'h3', 'h4']) or item.find('a', class_=lambda x: x and 'title' in str(x).lower() if x else True)
                    
                    if not title_elem:
                        continue
                        
                    title_text = title_elem.text.strip()
                    if not any(keyword in title_text.lower() for keyword in ['scholarship', 'fellowship']):
                        continue
                        
                    # Extract description and other details
                    desc_elem = item.find(['div', 'p'], class_=lambda x: x and any(word in str(x).lower() for word in ['content', 'desc', 'text']) if x else True)
                    desc_text = desc_elem.text.strip() if desc_elem else ''
                    
                    # Determine education level
                    education_level = 'ALL'
                    if any(word in title_text.lower() for word in ['phd', 'doctorate']):
                        education_level = 'PHD'
                    elif any(word in title_text.lower() for word in ['master']):
                        education_level = 'MASTERS'
                    elif any(word in title_text.lower() for word in ['undergraduate', 'bachelor']):
                        education_level = 'UNDERGRADUATE'
                    elif any(word in title_text.lower() for word in ['postdoc', 'post-doc']):
                        education_level = 'POSTDOC'
                    
                    # Extract requirements
                    requirements = [
                        'Must be a citizen of a Commonwealth country',
                        'Must have completed required academic qualifications by start date',
                        'Must meet English language requirements',
                        'Must be unable to afford to study in the UK without this scholarship',
                        'Must return to home country after the scholarship ends'
                    ]
                    if education_level == 'MASTERS':
                        requirements.append('Must hold a first degree of at least upper second class (2:1) standard')
                    elif education_level == 'PHD':
                        requirements.extend([
                            'Must hold a first degree of at least upper second class (2:1) standard',
                            'Must hold a Master\'s degree'
                        ])
                    
                    # Get URL
                    url = None
                    if isinstance(title_elem, Tag) and title_elem.name == 'a' and title_elem.has_attr('href'):
                        url = title_elem['href']
                    elif title_elem.find_parent('a') and title_elem.find_parent('a').has_attr('href'):
                        url = title_elem.find_parent('a')['href']
                    
                    if url and not url.startswith('http'):
                        url = 'https://cscuk.fcdo.gov.uk' + url
                    
                    scholarship = {
                        'title': title_text,
                        'organization': 'Commonwealth Scholarship Commission',
                        'description': desc_text if desc_text else f'Commonwealth {education_level.title() if education_level != "ALL" else ""} Scholarship opportunity for citizens of Commonwealth countries to study in the UK.',
                        'requirements': '\n'.join(requirements),
                        'amount': 'Full scholarship including:\n- Full tuition fees\n- Living allowance (stipend)\n- Return flights\n- Study travel grant\n- Initial arrival allowance\n- Research support grant (if applicable)\n- Family allowance (if applicable)\n- Excess baggage allowance\n- Thesis grant (for doctoral scholars)',
                        'country': 'United Kingdom',
                        'education_level': education_level,
                        'field_of_study': field_of_study or 'All Fields',
                        'deadline': None,
                        'website_url': url or 'https://cscuk.fcdo.gov.uk/scholarships/',
                        'source_website': 'Commonwealth Scholarship Commission',
                        'is_fully_funded': True,
                        'is_active': True
                    }
                    scholarships.append(scholarship)
                    logger.info(f'Found Commonwealth scholarship: {scholarship["title"]}')
        except Exception as e:
            logger.error(f"Error fetching Commonwealth scholarships: {str(e)}", exc_info=True)

        return scholarships

    def _get_daad_scholarships(self, field_of_study=None, country=None) -> List[Dict[str, Any]]:
        """Fetch scholarships from DAAD. This is a placeholder with sample data until we can access their API."""
        scholarships = [
            {
                'title': 'DAAD Research Grants - Doctoral Programmes in Germany',
                'organization': 'DAAD',
                'description': 'Research grants for highly qualified international doctoral candidates and young academics and scientists who plan to earn a doctoral degree in Germany.',
                'requirements': '- Master\'s degree or equivalent\n- Academic transcripts\n- Research proposal\n- Letter of acceptance from German supervisor\n- Language proficiency (German or English)',
                'amount': 'Monthly payment of €1,200\nHealth insurance, travel allowance, one-off study allowance',
                'country': 'Germany',
                'education_level': 'PHD',
                'field_of_study': field_of_study or 'All Fields',
                'deadline': None,
                'website_url': 'https://www.daad.de/en/study-and-research-in-germany/scholarships/',
                'source_website': 'DAAD',
                'is_fully_funded': True,
                'is_active': True
            },
            {
                'title': 'DAAD Master\'s Scholarships for Development-Related Postgraduate Courses',
                'organization': 'DAAD',
                'description': 'Scholarships for postgraduate studies at German universities in specific development-related courses.',
                'requirements': '- Bachelor\'s degree\n- At least two years of professional experience\n- IELTS/TOEFL score\n- Motivation letter',
                'amount': 'Monthly payment of €850\nHealth insurance, travel allowance, rent subsidy',
                'country': 'Germany',
                'education_level': 'MASTERS',
                'field_of_study': field_of_study or 'All Fields',
                'deadline': None,
                'website_url': 'https://www.daad.de/en/study-and-research-in-germany/scholarships/',
                'source_website': 'DAAD',
                'is_fully_funded': True,
                'is_active': True
            }
        ]
        return scholarships

    def _get_sweden_scholarships(self) -> List[Dict[str, Any]]:
        """Return Swedish Institute scholarships. This is a placeholder with sample data."""
        return [
            {
                'title': 'Swedish Institute Scholarships for Global Professionals (SISGP)',
                'organization': 'Swedish Institute',
                'description': 'The Swedish Institute Scholarships for Global Professionals (SISGP) programme offers full-time scholarships for master\'s degree studies in Sweden.',
                'requirements': '- Bachelor\'s degree\n- Work experience\n- Leadership experience\n- English proficiency (IELTS/TOEFL)\n- Citizenship of an eligible country',
                'amount': '- Tuition fee waiver\n- Monthly stipend of SEK 10,000\n- Travel grant of SEK 15,000\n- Insurance coverage',
                'country': 'Sweden',
                'education_level': 'MASTERS',
                'field_of_study': 'All Fields',
                'deadline': None,
                'website_url': 'https://si.se/en/apply/scholarships/',
                'source_website': 'Swedish Institute',
                'is_fully_funded': True,
                'is_active': True
            },
            {
                'title': 'SI PhD Programmes for Research in Sweden',
                'organization': 'Swedish Institute',
                'description': 'Doctoral scholarships for highly qualified international students to pursue research studies in Sweden.',
                'requirements': '- Master\'s degree\n- Research proposal\n- Acceptance from Swedish university\n- English proficiency\n- Citizenship requirements',
                'amount': '- Full tuition coverage\n- Monthly stipend\n- Travel grant\n- Health insurance',
                'country': 'Sweden',
                'education_level': 'PHD',
                'field_of_study': 'All Fields',
                'deadline': None,
                'website_url': 'https://si.se/en/apply/scholarships/',
                'source_website': 'Swedish Institute',
                'is_fully_funded': True,
                'is_active': True
            }
        ]

    def _get_cordis_scholarships(self, field_of_study=None, country=None, num_pages=1) -> List[Dict[str, Any]]:
        """
        Fetch scholarships from CORDIS public API for EU research funding
        """
        scholarships = []
        api_url = "https://api.tech.ec.europa.eu/funding/grants/grants"

        for page in range(num_pages):
            params = {
                'page': page + 1,
                'limit': 25,
                'orderBy': 'publicationDate',
                'order': 'desc',
                'language': 'en',
                'responseType': 'json'
            }
            if field_of_study:
                params['topic'] = field_of_study
            if country:
                params['country'] = country

            try:
                # Add required headers for the EU API
                headers = {
                    'Accept': 'application/json',
                    'User-Agent': 'OpportunityHub/1.0 (Educational Project)'
                }
                response = self.session.get(api_url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

                for item in data.get('results', []):
                    funding_info = item.get('fundingInformation', {})
                    topic_info = item.get('topic', {})
                    deadline_info = item.get('deadline', {})
                    
                    scholarship = {
                        'title': item.get('title', {}).get('en', 'Untitled Grant'),
                        'organization': item.get('fundingBody', 'European Commission'),
                        'description': item.get('description', {}).get('en', ''),
                        'requirements': item.get('eligibilityCriteria', {}).get('en', ''),
                        'amount': f"Maximum {funding_info.get('maxAmount', 'N/A')} EUR",
                        'country': 'European Union',
                        'education_level': self._map_cordis_level(topic_info.get('type')),
                        'field_of_study': topic_info.get('name', {}).get('en', 'Various'),
                        'deadline': self._parse_date(deadline_info.get('date')),
                        'website_url': item.get('callUrl'),
                        'source_website': 'EU Funding & Tenders',
                        'is_fully_funded': funding_info.get('fundingRate', 0) == 100,
                        'is_active': deadline_info.get('status') == 'OPEN'
                    }
                    scholarships.append(scholarship)

            except Exception as e:
                logger.error(f"Error in EU Funding API: {str(e)}")
                break

        return scholarships

    def _parse_date(self, date_string):
        """Parse various date formats"""
        if not date_string:
            return None
            
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00')).date()
        except:
            try:
                from dateutil import parser
                return parser.parse(date_string).date()
            except:
                return None

    def _map_daad_level(self, level):
        """Map DAAD education levels to our format"""
        if not level:
            return 'ALL'
        level = level.lower()
        if 'phd' in level or 'doctorate' in level:
            return 'PHD'
        if 'master' in level:
            return 'MASTERS'
        if 'bachelor' in level:
            return 'UNDERGRADUATE'
        if 'postdoc' in level:
            return 'POSTDOC'
        return 'ALL'

    def _map_cordis_level(self, level):
        """Map CORDIS education levels to our format"""
        if not level:
            return 'ALL'
        level = level.lower()
        # Check for postdoctoral first to avoid matching with doctoral
        if 'postdoc' in level or 'postdoctoral' in level:
            return 'POSTDOC'
        if any(x in level for x in ['early stage researcher', 'phd candidate', 'doctoral']):
            return 'PHD'
        if 'master' in level:
            return 'MASTERS'
        if 'undergraduate' in level or 'bachelor' in level:
            return 'UNDERGRADUATE'
        return 'ALL'

    def _extract_requirements_from_description(self, description):
        """Extract requirements from text description"""
        requirements = []
        text = description.lower()
        
        # Look for common requirement indicators
        indicators = [
            'requirements:', 
            'eligible:', 
            'eligibility:', 
            'you must:', 
            'applicants should'
        ]
        
        for indicator in indicators:
            if indicator in text:
                start = text.index(indicator) + len(indicator)
                end = text.find('.', start)
                if end != -1:
                    requirement = description[start:end].strip()
                    if requirement:
                        requirements.append(requirement)
                        
        return '\n'.join(requirements) if requirements else "Requirements not specified"

    def _extract_amount_from_description(self, description):
        """Extract scholarship amount from description"""
        text = description.lower()
        amount_indicators = ['sek', 'eur', '€', 'kr', 'amount', 'funding']
        
        for indicator in amount_indicators:
            if indicator in text:
                start = max(0, text.index(indicator) - 20)
                end = min(len(text), text.index(indicator) + 50)
                context = description[start:end]
                return context.strip()
                
        return "Amount not specified"

    def _extract_level_from_description(self, description):
        """Extract education level from description"""
        text = description.lower()
        if 'phd' in text or 'doctorate' in text:
            return 'PHD'
        if 'master' in text:
            return 'MASTERS'
        if 'bachelor' in text or 'undergraduate' in text:
            return 'UNDERGRADUATE'
        if 'postdoc' in text:
            return 'POSTDOC'
        return 'ALL'