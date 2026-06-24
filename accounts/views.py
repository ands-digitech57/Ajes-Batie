import logging
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from profiles.models import Profile, Skill
from .forms import SignUpForm
from .models import Notification

logger = logging.getLogger(__name__)


def _get_skills_from_text(skills_text):
    """
    Convertit une chaîne de compétences séparées par des virgules
    en objets Skill de manière propre et sécurisée.
    """
    if not skills_text:
        return []
        
    # Extraction, passage en minuscules et suppression des espaces inutiles
    names = {
        item.strip().lower()
        for item in skills_text.split(",")
        if item.strip()
    }

    skills = []
    for name in names:
        skill, _ = Skill.objects.get_or_create(name=name)
        skills.append(skill)

    return skills


def signup(request):
    """
    Gère l'inscription des utilisateurs et la création simultanée
    de leur profil professionnel dans une transaction atomique.
    """
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # Utilisation d'un bloc atomique pour garantir la cohérence des données
                with transaction.atomic():
                    # 1. Création de l'utilisateur standard Django
                    user = form.save()

                    # 2. Création du profil lié avec les champs complémentaires
                    profile = Profile.objects.create(
                        user=user,
                        email=form.cleaned_data.get("email") or user.email,
                        job_title=form.cleaned_data.get("job_title", ""),
                        current_company=form.cleaned_data.get("current_company", ""),
                        industry=form.cleaned_data.get("industry", ""),
                        bio=form.cleaned_data.get("bio", ""),
                        status=form.cleaned_data.get("status") or "available",
                        education_level=form.cleaned_data.get("education_level", ""),
                        location=form.cleaned_data.get("location", ""),
                        phone=form.cleaned_data.get("phone", ""),
                        whatsapp=form.cleaned_data.get("whatsapp", ""),
                        linkedin_url=form.cleaned_data.get("linkedin_url", ""),
                        photo_url=form.cleaned_data.get("photo_url", ""),
                        is_public=form.cleaned_data.get("is_public", True),
                        cv_file=form.cleaned_data.get("cv_file"),
                    )

                    # 3. Gestion optionnelle de l'image de profil
                    photo_file = form.cleaned_data.get("photo_file")
                    if photo_file:
                        profile.photo_file = photo_file
                        profile.save(update_fields=["photo_file"])

                    # 4. Correction du nom du champ : 'skills_text' au lieu de 'skills'
                    skills_raw = form.cleaned_data.get("skills_text", "")
                    skills = _get_skills_from_text(skills_raw)
                    if skills:
                        profile.skills.set(skills)

                # Connexion automatique après inscription réussie
                login(request, user)
                messages.success(request, "Votre compte a été créé avec succès. Bienvenue sur Ajes Connect !")
                return redirect("/")

            except Exception as e:
                logger.exception(f"Erreur système critique lors de l'inscription de l'utilisateur: {e}")
                form.add_error(
                    None,
                    "Une erreur système est survenue pendant la création de votre compte. Veuillez réessayer."
                )
    else:
        form = SignUpForm()

    return render(
        request,
        "accounts/signup.html",
        {"form": form},
    )


@login_required
def dashboard(request):
    """
    Affiche l'espace personnel de l'utilisateur avec ses candidatures récentes.
    """
    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            "email": request.user.email,
            "is_public": True,
        },
    )

    # Récupération optimisée des 5 dernières candidatures
    applications = (
        profile.applications
        .select_related("job_offer")
        .order_by("-id")[:5]
    )

    return render(
        request,
        "accounts/dashboard.html",
        {
            "profile": profile,
            "applications": applications,
        },
    )


@login_required
def notifications(request):
    """
    Affiche les notifications de l'utilisateur et les marque comme lues.
    """
    # 1. On récupère d'abord le QuerySet pour l'affichage (conserve l'état non-lu dans le template)
    notifications_list = (
        Notification.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    # Force l'évaluation immédiate du statut pour le template avant la mise à jour en BDD
    notifications_qs = list(notifications_list)

    # 2. Ensuite, on bascule silencieusement toutes les notifications non-lues à lues en BDD
    Notification.objects.filter(
        user=request.user,
        is_read=False,
    ).update(is_read=True)

    return render(
        request,
        "accounts/notifications.html",
        {
            "notifications": notifications_qs,
        },
    )