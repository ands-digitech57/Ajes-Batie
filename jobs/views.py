from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import Notification
from profiles.models import Profile
from .forms import ApplicationForm, JobOfferForm
from .models import Application, JobOffer


@login_required
def job_list(request):
    query = request.GET.get('q', '').strip()
    jobs = JobOffer.objects.filter(is_active=True)

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query)
            | Q(company_name__icontains=query)
            | Q(location__icontains=query)
            | Q(required_skills__icontains=query)
            | Q(description__icontains=query)
        )

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'query': query,
    })


@login_required
def job_detail(request, pk):
    job = get_object_or_404(JobOffer, pk=pk, is_active=True)
    has_applied = False

    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        if profile:
            has_applied = Application.objects.filter(job_offer=job, profile=profile).exists()

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'has_applied': has_applied,
    })


@login_required
def job_create(request):
    if not request.user.is_staff:
        messages.error(request, "Vous n'êtes pas autorisé à publier des offres.")
        return redirect('jobs:list')

    if request.method == 'POST':
        form = JobOfferForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                job = form.save()
                recipients = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
                notifications = [
                    Notification(
                        user=user,
                        title="Nouvelle offre d'emploi",
                        message=f"Une nouvelle offre '{job.title}' a été publiée.",
                        link=job.get_absolute_url(),
                        type='job',
                    )
                    for user in recipients
                ]
                Notification.objects.bulk_create(notifications)
            messages.success(request, "Votre offre a ete publiee.")
            return redirect(job)
    else:
        form = JobOfferForm()

    return render(request, 'jobs/job_form.html', {'form': form})


@login_required
def job_apply(request, pk):
    job = get_object_or_404(JobOffer, pk=pk, is_active=True)
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'email': request.user.email, 'is_public': True},
    )

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job_offer = job
            application.profile = profile
            try:
                application.save()
            except IntegrityError:
                messages.info(request, 'Vous avez deja postule a cette offre.')
            else:
                messages.success(request, 'Votre candidature a ete envoyee.')
            return redirect(job)
    else:
        form = ApplicationForm()

    return render(request, 'jobs/application_form.html', {
        'form': form,
        'job': job,
        'profile': profile,
    })
