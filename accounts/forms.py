import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from profiles.models import Profile
from profiles.validators import validate_cv_file

# Regex robuste pour la validation des numéros de téléphone
PHONE_REGEX = re.compile(r'^\+?[0-9 ]{8,20}$')

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        label="Prénom",
        max_length=150,
        required=True,
    )
    last_name = forms.CharField(
        label="Nom",
        max_length=150,
        required=True,
    )
    email = forms.EmailField(
        label="Email",
        required=True,
    )
    job_title = forms.CharField(
        label="Titre professionnel",
        required=False,
    )
    current_company = forms.CharField(
        label="Entreprise actuelle",
        required=False,
    )
    industry = forms.CharField(
        label="Secteur",
        required=False,
    )
    bio = forms.CharField(
        label="Présentation",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Décrivez votre parcours..."
            }
        ),
    )
    skills_text = forms.CharField(
        label="Compétences",
        required=False,
    )
    status = forms.ChoiceField(
        label="Statut actuel",
        choices=Profile.Status.choices,  # <-- CORRECTION ICI : Utilisation de la classe TextChoices
        required=False,
        initial=Profile.Status.AVAILABLE,
    )
    education_level = forms.CharField(
        label="Niveau d'études",
        required=False,
    )
    location = forms.CharField(
        label="Localisation",
        required=False,
    )
    phone = forms.CharField(
        label="Téléphone",
        required=False,
    )
    whatsapp = forms.CharField(
        label="WhatsApp",
        required=False,
    )
    linkedin_url = forms.URLField(
        label="Lien LinkedIn",
        required=False,
    )
    photo_file = forms.ImageField(
        label="Photo de profil",
        required=False,  # <-- SANS LE VALIDATEUR LOCAL qui entrait en conflit avec Cloudinary
    )
    photo_url = forms.URLField(
        label="URL de la photo",
        required=False,
    )
    cv_file = forms.FileField(
        label="Curriculum Vitae",
        required=False,
        validators=[validate_cv_file],
    )
    is_public = forms.BooleanField(
        label="Rendre mon profil visible publiquement",
        required=False,
        initial=True,
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )

    def clean_username(self):
        username = self.cleaned_data["username"].strip().lower()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Ce nom d'utilisateur existe déjà.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and not PHONE_REGEX.match(phone):
            raise ValidationError("Numéro de téléphone invalide.")
        return phone

    def clean_whatsapp(self):
        whatsapp = self.cleaned_data.get("whatsapp")
        if whatsapp and not PHONE_REGEX.match(whatsapp):
            raise ValidationError("Numéro WhatsApp invalide.")
        return whatsapp

    def clean_linkedin_url(self):
        url = self.cleaned_data.get("linkedin_url")
        if url and "linkedin.com" not in url.lower():
            raise ValidationError("Veuillez saisir un lien LinkedIn valide.")
        return url

    def clean(self):
        cleaned_data = super().clean()
        photo_file = cleaned_data.get("photo_file")
        photo_url = cleaned_data.get("photo_url")

        if photo_file and photo_url:
            raise ValidationError(
                "Choisissez soit une photo téléchargée, soit une URL."
            )
        return cleaned_data