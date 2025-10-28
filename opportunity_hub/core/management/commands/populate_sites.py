from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    help = 'Populates the Sites framework with job and scholarship websites'

    def handle(self, *args, **kwargs):
        # Dictionary of sites to create/update
        sites_data = {
            'opportunity_hub': {
                'domain': 'opportunity-hub.example.com',
                'name': 'Opportunity Hub'
            },
            'indeed': {
                'domain': 'www.indeed.com',
                'name': 'Indeed'
            },
            'linkedin': {
                'domain': 'www.linkedin.com',
                'name': 'LinkedIn'
            },
            'remoteok': {
                'domain': 'remoteok.com',
                'name': 'RemoteOK'
            },
            'glassdoor': {
                'domain': 'www.glassdoor.com',
                'name': 'Glassdoor'
            },
            'scholarships_com': {
                'domain': 'www.scholarships.com',
                'name': 'Scholarships.com'
            },
            'fulbright': {
                'domain': 'foreign.fulbrightonline.org',
                'name': 'Fulbright Program'
            },
            'erasmus': {
                'domain': 'erasmus-plus.ec.europa.eu',
                'name': 'Erasmus+ Programme'
            },
            'daad': {
                'domain': 'www.daad.de',
                'name': 'DAAD Scholarships'
            },
            'chevening': {
                'domain': 'www.chevening.org',
                'name': 'Chevening Scholarships'
            }
        }

        # Create or update sites
        for key, data in sites_data.items():
            site, created = Site.objects.get_or_create(
                domain=data['domain'],
                defaults={'name': data['name']}
            )
            
            if not created:
                site.name = data['name']
                site.save()
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(f'{action} site: {site.name} ({site.domain})')
            )

        # Set the default site
        default_site = Site.objects.get(domain='opportunity-hub.example.com')
        settings.SITE_ID = default_site.id
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSet default site to: {default_site.name}')
        )

        # Print summary
        self.stdout.write('\nSummary of available sites:')
        for site in Site.objects.all().order_by('name'):
            self.stdout.write(f'- {site.name} (ID: {site.id}, Domain: {site.domain})')