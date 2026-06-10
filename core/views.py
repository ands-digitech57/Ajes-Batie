from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from jobs.models import JobOffer
from journal.models import JournalPost
from profiles.models import Profile


@login_required
def home(request):
    context = {
        'profile_count': Profile.objects.filter(is_public=True).count(),
        'job_count': JobOffer.objects.filter(is_active=True).count(),
        'latest_jobs': JobOffer.objects.filter(is_active=True)[:3],
        'latest_posts': JournalPost.objects.filter(is_published=True)[:3],
    }
    return render(request, 'core/home.html', context)
