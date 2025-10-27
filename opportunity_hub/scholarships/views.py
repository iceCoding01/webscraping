from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect
from .models import Scholarship, ScholarshipApplication
from .tasks import scrape_scholarships_task

class ScholarshipListView(ListView):
    model = Scholarship
    template_name = 'scholarships/scholarship_list.html'
    context_object_name = 'scholarships'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by search query
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(organization__icontains=q) |
                Q(description__icontains=q)
            )
        
        # Filter by education level
        education_level = self.request.GET.get('education_level')
        if education_level:
            queryset = queryset.filter(education_level=education_level)
            
        # Filter by country
        country = self.request.GET.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)
            
        # Filter by field of study
        field = self.request.GET.get('field')
        if field:
            queryset = queryset.filter(field_of_study__icontains=field)
            
        # Filter by fully funded
        fully_funded = self.request.GET.get('fully_funded')
        if fully_funded:
            queryset = queryset.filter(is_fully_funded=True)
            
        return queryset

class ScholarshipDetailView(DetailView):
    model = Scholarship
    template_name = 'scholarships/scholarship_detail.html'
    context_object_name = 'scholarship'

class ScholarshipApplicationCreateView(LoginRequiredMixin, CreateView):
    model = ScholarshipApplication
    template_name = 'scholarships/scholarship_application_form.html'
    fields = ['status', 'notes', 'applied_date']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.scholarship_id = self.kwargs['scholarship_id']
        return super().form_valid(form)

class ScholarshipApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = ScholarshipApplication
    template_name = 'scholarships/scholarship_application_form.html'
    fields = ['status', 'notes', 'applied_date']

def scholarship_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
        
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
