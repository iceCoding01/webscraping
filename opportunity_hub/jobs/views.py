from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import JobListing, JobApplication
from django.contrib import messages

def job_list(request):
    jobs = JobListing.objects.all().order_by('-posted_date')
    
    # Handle search and filters
    q = request.GET.get('q')
    if q:
        jobs = jobs.filter(
            Q(title__icontains=q) |
            Q(company__icontains=q) |
            Q(description__icontains=q)
        )
    
    employment_type = request.GET.get('employment_type')
    if employment_type:
        jobs = jobs.filter(employment_type=employment_type)
        
    location = request.GET.get('location')
    if location:
        jobs = jobs.filter(location__icontains=location)
        
    remote_only = request.GET.get('remote_only')
    if remote_only:
        jobs = jobs.filter(is_remote=True)
    
    context = {
        'jobs': jobs,
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, pk):
    job = get_object_or_404(JobListing, pk=pk)
    context = {
        'job': job,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def dashboard(request):
    applications = JobApplication.objects.filter(user=request.user).select_related('job')
    saved_jobs = applications.filter(status='SAVED')
    applied_jobs = applications.filter(status='APPLIED')
    in_progress_jobs = applications.filter(status='IN_PROGRESS')
    
    context = {
        'saved_jobs': saved_jobs,
        'applied_jobs': applied_jobs,
        'in_progress_jobs': in_progress_jobs,
    }
    return render(request, 'jobs/dashboard.html', context)

@login_required
def job_apply(request, pk):
    job = get_object_or_404(JobListing, pk=pk)
    
    # Check if already applied
    if JobApplication.objects.filter(user=request.user, job=job).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs:job-detail', pk=pk)
    
    # Create new application
    JobApplication.objects.create(
        user=request.user,
        job=job,
        status='APPLIED'
    )
    
    messages.success(request, 'Successfully applied for the job!')
    return redirect('jobs:dashboard')
