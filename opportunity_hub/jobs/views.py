from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import JobListing, JobApplication
from .tasks import scrape_jobs_task

class JobListView(ListView):
    model = JobListing
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10
    ordering = ['-posted_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by search query
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(company__icontains=q) |
                Q(description__icontains=q)
            )
        
        # Filter by employment type
        employment_type = self.request.GET.get('employment_type')
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)
            
        # Filter by location
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        # Filter by remote only
        remote_only = self.request.GET.get('remote_only')
        if remote_only:
            queryset = queryset.filter(is_remote=True)
            
        return queryset

class JobDetailView(DetailView):
    model = JobListing
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

class JobApplicationCreateView(LoginRequiredMixin, CreateView):
    model = JobApplication
    template_name = 'jobs/job_application_form.html'
    fields = ['status', 'notes', 'applied_date']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.job_id = self.kwargs['job_id']
        return super().form_valid(form)

class JobApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = JobApplication
    template_name = 'jobs/job_application_form.html'
    fields = ['status', 'notes', 'applied_date']

def job_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
        
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
