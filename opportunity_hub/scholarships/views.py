from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Scholarship, ScholarshipApplication

def scholarship_list(request):
    scholarships = Scholarship.objects.all().order_by('-created_at')
    
    # Filter by search query
    q = request.GET.get('q')
    if q:
        scholarships = scholarships.filter(
            Q(title__icontains=q) |
            Q(organization__icontains=q) |
            Q(description__icontains=q)
        )
    
    # Filter by education level
    education_level = request.GET.get('education_level')
    if education_level:
        scholarships = scholarships.filter(education_level=education_level)
        
    # Filter by country
    country = request.GET.get('country')
    if country:
        scholarships = scholarships.filter(country__icontains=country)
        
    # Filter by field of study
    field = request.GET.get('field')
    if field:
        scholarships = scholarships.filter(field_of_study__icontains=field)
        
    # Filter by fully funded
    fully_funded = request.GET.get('fully_funded')
    if fully_funded:
        scholarships = scholarships.filter(is_fully_funded=True)
    
    context = {
        'scholarships': scholarships,
    }
    return render(request, 'scholarships/scholarship_list.html', context)

def scholarship_detail(request, pk):
    scholarship = get_object_or_404(Scholarship, pk=pk)
    similar_scholarships = Scholarship.objects.filter(
        Q(education_level=scholarship.education_level) |
        Q(field_of_study=scholarship.field_of_study)
    ).exclude(pk=scholarship.pk)[:3]
    
    context = {
        'scholarship': scholarship,
        'similar_scholarships': similar_scholarships,
    }
    return render(request, 'scholarships/scholarship_detail.html', context)

@login_required
def dashboard(request):
    applications = ScholarshipApplication.objects.filter(user=request.user).select_related('scholarship')
    saved_scholarships = applications.filter(status='SAVED')
    applied_scholarships = applications.filter(status='APPLIED')
    in_progress_scholarships = applications.filter(status='IN_PROGRESS')
    
    context = {
        'saved_scholarships': saved_scholarships,
        'applied_scholarships': applied_scholarships,
        'in_progress_scholarships': in_progress_scholarships,
    }
    return render(request, 'scholarships/dashboard.html', context)

@login_required
def scholarship_apply(request, pk):
    scholarship = get_object_or_404(Scholarship, pk=pk)
    
    # Check if already applied
    if ScholarshipApplication.objects.filter(user=request.user, scholarship=scholarship).exists():
        messages.warning(request, 'You have already applied for this scholarship.')
        return redirect('scholarships:scholarship-detail', pk=pk)
    
    # Create new application
    ScholarshipApplication.objects.create(
        user=request.user,
        scholarship=scholarship,
        status='APPLIED'
    )
    
    messages.success(request, 'Successfully applied for the scholarship!')
    return redirect('scholarships:dashboard')
