from django.contrib import admin
from .models import Application, JobOffer


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'recruiter_name', 'location', 'is_active', 'created_at')
    list_filter = ('contract_type', 'is_active', 'created_at')
    search_fields = ('title', 'company_name', 'recruiter_name', 'description', 'required_skills')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job_offer', 'profile', 'created_at')
    search_fields = ('job_offer__title', 'profile__user__first_name', 'profile__user__last_name', 'message')
