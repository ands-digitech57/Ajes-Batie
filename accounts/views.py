from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db import transaction
from profiles.models import Profile, Skill
from .forms import SignUpForm
from .models import Notification
import traceback  # <-- À ajouter tout en haut pour voir les erreurs détaillées


def _get_skills_from_text(skills_text):
    names = [item.strip().lower() for item in (skills_text or '').split(',') if item.strip()]
    skills = []
    for name in names:
        skill, _ = Skill.objects.get_or_create(name=name)
        skills.append(skill)
    return skills


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    profile = Profile.objects.create(
                        user=user,
                        email=form.cleaned_data.get('email') or user.email,
                        job_title=form.cleaned_data.get('job_title', ''),
                        current_company=form.cleaned_data.get('current_company', ''),
                        industry=form.cleaned_data.get('industry', ''),
                        bio=form.cleaned_data.get('bio', ''),
                        status=form.cleaned_data.get('status') or 'available',
                        education_level=form.cleaned_data.get('education_level', ''),
                        location=form.cleaned_data.get('location', ''),
                        phone=form.cleaned_data.get('phone', ''),
                        whatsapp=form.cleaned_data.get('whatsapp', ''),
                        linkedin_url=form.cleaned_data.get('linkedin_url', ''),
                        photo_url=form.cleaned_data.get('photo_url', ''),
                        is_public=form.cleaned_data.get('is_public', True),
                        cv_file=form.cleaned_data.get('cv_file'),
                    )
                    photo_file = form.cleaned_data.get('photo_file')
                    if photo_file:
                        profile.photo_file = photo_file
                        profile.save()

                    skills = _get_skills_from_text(form.cleaned_data.get('skills_text'))
                    if skills:
                        profile.skills.set(skills)

                login(request, user)
                return redirect('dashboard')
                
            except Exception as e:
                # Si la base de données rejette l'inscription, l'erreur s'affichera sur votre site
                print("ERREUR CRITIQUÉ INSCRIPTION :", traceback.format_exc())
                form.add_error(None, f"Erreur système lors de l'enregistrement : {e}")
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'email': request.user.email, 'is_public': True},
    )
    applications = profile.applications.select_related('job_offer')[:5]
    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'applications': applications,
    })


@login_required
def notifications(request):
    notifications_qs = Notification.objects.filter(user=request.user).order_by('-created_at')
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return render(request, 'accounts/notifications.html', {
        'notifications': notifications_qs,
    })
