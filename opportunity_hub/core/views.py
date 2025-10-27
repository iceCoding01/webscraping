from django.shortcuts import render
from jobs.models import JobListing
from scholarships.models import Scholarship

def home(request):
    latest_jobs = JobListing.objects.filter(is_active=True).order_by('-posted_date')[:6]
    latest_scholarships = Scholarship.objects.filter(is_active=True).order_by('-created_at')[:6]
    
    context = {
        'latest_jobs': latest_jobs,
        'latest_scholarships': latest_scholarships,
    }
    return render(request, 'core/home.html', context)
