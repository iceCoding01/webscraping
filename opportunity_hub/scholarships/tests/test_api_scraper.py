import pytest
from unittest.mock import Mock, patch
from opportunity_hub.scholarships.scrapers.api_scraper import APIScholarshipScraper
from datetime import datetime
import json

@pytest.fixture
def api_scraper():
    return APIScholarshipScraper()

def test_daad_scholarships(api_scraper):
    mock_response = Mock()
    mock_response.json.return_value = {
        'items': [{
            'title': 'Test DAAD Scholarship',
            'description': 'Test description',
            'requirements': 'Test requirements',
            'funding': 'Full scholarship',
            'destination': 'Germany',
            'degree': 'PhD',
            'subject': 'Computer Science',
            'deadline': '2024-12-31',
            'url': 'https://test.daad.de'
        }]
    }
    mock_response.status_code = 200

    with patch('requests.Session.get', return_value=mock_response):
        scholarships = api_scraper._get_daad_scholarships()
        
        assert len(scholarships) == 1
        scholarship = scholarships[0]
        assert scholarship['title'] == 'Test DAAD Scholarship'
        assert scholarship['organization'] == 'DAAD'
        assert scholarship['country'] == 'Germany'
        assert scholarship['education_level'] == 'PHD'
        assert scholarship['is_fully_funded'] == True

def test_sweden_scholarships(api_scraper):
    mock_response = Mock()
    mock_response.content = '''<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <item>
                <title>Swedish Institute Scholarship</title>
                <description>Full scholarship for Master's studies. Requirements: Bachelor's degree</description>
                <link>https://test.si.se</link>
                <pubDate>Wed, 31 Dec 2024 12:00:00 GMT</pubDate>
            </item>
        </channel>
    </rss>'''
    mock_response.status_code = 200

    with patch('requests.Session.get', return_value=mock_response):
        scholarships = api_scraper._get_sweden_scholarships()
        
        assert len(scholarships) == 1
        scholarship = scholarships[0]
        assert scholarship['title'] == 'Swedish Institute Scholarship'
        assert scholarship['organization'] == 'Swedish Institute'
        assert scholarship['country'] == 'Sweden'
        assert scholarship['education_level'] == 'MASTERS'
        assert scholarship['website_url'] == 'https://test.si.se'

def test_cordis_scholarships(api_scraper):
    mock_response = Mock()
    mock_response.json.return_value = {
        'results': [{
            'title': 'Test CORDIS Scholarship',
            'organization': 'Test University',
            'objective': 'Research scholarship',
            'eligibility': 'PhD candidates',
            'fundingDetails': 'Full funding',
            'hostCountry': 'Netherlands',
            'academicLevel': 'early stage researcher',
            'topic': 'Computer Science',
            'deadline': '2024-12-31',
            'infoUrl': 'https://test.cordis.eu'
        }]
    }
    mock_response.status_code = 200

    with patch('requests.Session.get', return_value=mock_response):
        scholarships = api_scraper._get_cordis_scholarships()
        
        assert len(scholarships) == 1
        scholarship = scholarships[0]
        assert scholarship['title'] == 'Test CORDIS Scholarship'
        assert scholarship['organization'] == 'Test University'
        assert scholarship['country'] == 'Netherlands'
        assert scholarship['education_level'] == 'PHD'
        assert scholarship['is_fully_funded'] == True

def test_scrape_scholarships_integration(api_scraper):
    """Test the main scraping method that combines all sources"""
    with patch.object(api_scraper, '_get_daad_scholarships', return_value=[{'title': 'DAAD1'}]), \
         patch.object(api_scraper, '_get_sweden_scholarships', return_value=[{'title': 'Sweden1'}]), \
         patch.object(api_scraper, '_get_cordis_scholarships', return_value=[{'title': 'CORDIS1'}]):
        
        scholarships = api_scraper.scrape_scholarships()
        
        assert len(scholarships) == 3
        titles = [s['title'] for s in scholarships]
        assert 'DAAD1' in titles
        assert 'Sweden1' in titles
        assert 'CORDIS1' in titles

def test_error_handling(api_scraper):
    """Test that errors in one source don't affect others"""
    def raise_error(*args, **kwargs):
        raise Exception("Test error")

    with patch.object(api_scraper, '_get_daad_scholarships', side_effect=raise_error), \
         patch.object(api_scraper, '_get_sweden_scholarships', return_value=[{'title': 'Sweden1'}]), \
         patch.object(api_scraper, '_get_cordis_scholarships', return_value=[{'title': 'CORDIS1'}]):
        
        scholarships = api_scraper.scrape_scholarships()
        
        assert len(scholarships) == 2  # DAAD failed but others succeeded
        titles = [s['title'] for s in scholarships]
        assert 'Sweden1' in titles
        assert 'CORDIS1' in titles

def test_date_parsing():
    scraper = APIScholarshipScraper()
    
    # Test ISO format
    assert scraper._parse_date('2024-12-31T00:00:00Z') == datetime(2024, 12, 31).date()
    
    # Test RFC format
    assert scraper._parse_date('Wed, 31 Dec 2024 12:00:00 GMT') == datetime(2024, 12, 31).date()
    
    # Test invalid date
    assert scraper._parse_date('invalid date') is None
    assert scraper._parse_date(None) is None

def test_education_level_mapping():
    scraper = APIScholarshipScraper()
    
    # Test DAAD mappings
    assert scraper._map_daad_level('PhD') == 'PHD'
    assert scraper._map_daad_level('Master') == 'MASTERS'
    assert scraper._map_daad_level('Bachelor') == 'UNDERGRADUATE'
    assert scraper._map_daad_level(None) == 'ALL'
    
    # Test CORDIS mappings
    assert scraper._map_cordis_level('early stage researcher') == 'PHD'
    assert scraper._map_cordis_level('postdoctoral') == 'POSTDOC'
    assert scraper._map_cordis_level(None) == 'ALL'