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
from django.utils.text import slugify # Tout en haut de views.py


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
        return redirect("jobs:list")

    if request.method == "POST":
        form = JobOfferForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # 1. On prépare la sauvegarde sans envoyer immédiatement en base de données
                job = form.save(commit=False)
                
                # 2. Sécurité : Si votre modèle JobOffer requiert un slug, on le génère ici
                if hasattr(job, 'slug') and not job.slug:
                    job.slug = slugify(job.title)
                
                # 3. Sécurité : Si votre modèle JobOffer a un champ 'author' ou 'user', on l'associe
                if hasattr(job, 'author'):
                    job.author = request.user
                elif hasattr(job, 'user'):
                    job.user = request.user

                # 4. On enregistre définitivement l'offre en base de données
                job.save()
                form.save_m2m()  # Important si vous avez des champs ManyToMany

                # --- Le reste de votre code pour les notifications reste identique ---
                recipients = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
                Notification.objects.bulk_create([
                    Notification(
                        user=user,
                        title="Nouvelle offre d'emploi",
                        message=f"Une nouvelle offre '{job.title}' a été publiée.",
                        link=job.get_absolute_url(),
                        type="job",
                    )
                    for user in recipients
                ])

            messages.success(request, "Votre offre a été publiée.")
            return redirect(job)
        else:
            # Si le formulaire n'est pas valide, on prévient l'admin par un message
            messages.error(request, "Le formulaire contient des erreurs. Veuillez vérifier les champs.")
    else:
        form = JobOfferForm()

    return render(request, "jobs/job_form.html", {"form": form})

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

