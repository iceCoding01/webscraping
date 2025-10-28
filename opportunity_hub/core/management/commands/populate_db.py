from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from jobs.models import JobListing, JobApplication
from scholarships.models import Scholarship, ScholarshipApplication
import random

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # Create or get sample users
        self.stdout.write('Creating sample users...')
        users = []
        for i in range(3):
            username = f'user{i+1}'
            email = f'user{i+1}@example.com'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            users.append(user)

        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('adminpass123')
            admin_user.save()
        users.append(admin_user)

        # Sample data for jobs
        companies = [
            'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Netflix', 'Twitter',
            'LinkedIn', 'Airbnb', 'Uber', 'Tesla', 'SpaceX', 'IBM', 'Intel', 'Oracle'
        ]

        locations = [
            'New York, USA', 'San Francisco, USA', 'London, UK', 'Berlin, Germany',
            'Paris, France', 'Tokyo, Japan', 'Singapore', 'Sydney, Australia',
            'Toronto, Canada', 'Amsterdam, Netherlands'
        ]

        job_titles = [
            'Software Engineer', 'Data Scientist', 'Product Manager', 'DevOps Engineer',
            'UI/UX Designer', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer',
            'Machine Learning Engineer', 'Cloud Architect', 'Mobile Developer',
            'System Administrator', 'QA Engineer', 'Business Analyst', 'Project Manager'
        ]

        employment_types = ['FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP']

        # Create sample jobs
        self.stdout.write('Creating sample jobs...')
        jobs = []
        for i in range(20):
            posted_date = datetime.now() - timedelta(days=random.randint(1, 30))
            deadline = posted_date + timedelta(days=random.randint(14, 60))
            salary_min = random.randint(50000, 100000)
            salary_max = salary_min + random.randint(20000, 50000)

            job = JobListing.objects.create(
                title=random.choice(job_titles),
                company=random.choice(companies),
                location=random.choice(locations),
                description=f'This is a sample job description for position {i+1}. '
                          f'We are looking for talented individuals to join our team.',
                requirements='- Bachelor\'s degree in Computer Science or related field\n'
                           '- 3+ years of experience in software development\n'
                           '- Strong problem-solving skills\n'
                           '- Excellent communication skills',
                employment_type=random.choice(employment_types),
                salary_range=f'${salary_min:,} - ${salary_max:,}',
                is_remote=random.choice([True, False]),
                posted_date=posted_date,
                deadline=deadline,
                application_url=f'https://example.com/jobs/{i+1}',
                source_website='Example.com'
            )
            jobs.append(job)

        # Create sample job applications
        self.stdout.write('Creating sample job applications...')
        for user in users:
            # Create a list of random jobs without duplicates
            random_jobs = random.sample(jobs, k=min(len(jobs), random.randint(2, 5)))
            for job in random_jobs:
                status = random.choice(['SAVED', 'APPLIED', 'IN_PROGRESS'])
                JobApplication.objects.create(
                    user=user,
                    job=job,
                    status=status,
                    applied_date=datetime.now() - timedelta(days=random.randint(1, 14)),
                    notes=f'Sample application notes for {job.title}'
                )

        # Sample data for scholarships
        organizations = [
            'Harvard University', 'MIT', 'Stanford University', 'Oxford University',
            'Cambridge University', 'ETH Zurich', 'National Science Foundation',
            'Fulbright Program', 'DAAD', 'British Council'
        ]

        countries = [
            'United States', 'United Kingdom', 'Germany', 'France', 'Australia',
            'Canada', 'Japan', 'Singapore', 'Switzerland', 'Netherlands'
        ]

        education_levels = ['UNDERGRADUATE', 'MASTERS', 'PHD']
        fields_of_study = [
            'Computer Science', 'Data Science', 'Artificial Intelligence',
            'Business Administration', 'Engineering', 'Mathematics',
            'Physics', 'Chemistry', 'Biology', 'Environmental Science'
        ]

        # Create sample scholarships
        self.stdout.write('Creating sample scholarships...')
        scholarships = []
        for i in range(20):
            created_at = datetime.now() - timedelta(days=random.randint(1, 30))
            deadline = created_at + timedelta(days=random.randint(30, 90))
            
            # Generate a random amount
            funding_amounts = [
                'Up to $10,000', '$5,000', '$20,000 - $30,000',
                'Full Tuition', '$15,000/year', '$25,000',
                '$40,000 + stipend', 'Varies',
                '$50,000 for entire program', '$10,000/semester'
            ]

            scholarship = Scholarship.objects.create(
                title=f'{random.choice(organizations)} Scholarship Program {i+1}',
                organization=random.choice(organizations),
                description=f'This is a sample scholarship description for program {i+1}. '
                          f'We are offering full/partial funding for outstanding students.',
                requirements='- Strong academic record\n'
                           '- Research proposal\n'
                           '- Letters of recommendation\n'
                           '- Language proficiency',
                education_level=random.choice(education_levels),
                field_of_study=random.choice(fields_of_study),
                country=random.choice(countries),
                amount=random.choice(funding_amounts),
                is_fully_funded=random.choice([True, False]),
                deadline=deadline,
                website_url=f'https://example.com/scholarships/{i+1}',
                source_website='Example.com'
            )
            scholarships.append(scholarship)

        # Create sample scholarship applications
        self.stdout.write('Creating sample scholarship applications...')
        for user in users:
            # Create a list of random scholarships without duplicates
            random_scholarships = random.sample(scholarships, k=min(len(scholarships), random.randint(2, 5)))
            for scholarship in random_scholarships:
                status = random.choice(['SAVED', 'APPLIED', 'IN_PROGRESS'])
                ScholarshipApplication.objects.create(
                    user=user,
                    scholarship=scholarship,
                    status=status,
                    applied_date=datetime.now() - timedelta(days=random.randint(1, 14)),
                    notes=f'Sample application notes for {scholarship.title}'
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data'))
        self.stdout.write('\nSample Users Created:')
        self.stdout.write('Admin user:')
        self.stdout.write('  Username: admin')
        self.stdout.write('  Password: adminpass123')
        self.stdout.write('\nRegular users:')
        for i in range(3):
            self.stdout.write(f'  Username: user{i+1}')
            self.stdout.write(f'  Password: testpass123')