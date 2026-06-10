from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from profiles.models import Profile
from profiles.validators import validate_image_file, validate_cv_file
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label='Prenom', max_length=150, required=True)
    last_name = forms.CharField(label='Nom', max_length=150, required=True)
    email = forms.EmailField(label='Email', required=True)
    job_title = forms.CharField(label='Titre professionnel', max_length=150, required=False)
    current_company = forms.CharField(label='Entreprise actuelle', max_length=150, required=False)
    industry = forms.CharField(label='Secteur', max_length=120, required=False)
    bio = forms.CharField(
        label='Presentation',
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Decrivez votre parcours et vos objectifs professionnels'}),
    )
    skills_text = forms.CharField(
        label='Competences',
        required=False,
        help_text='Separez les competences par des virgules.',
        widget=forms.TextInput(attrs={'placeholder': 'Ex: marketing, gestion de projet, design'}),
    )
    status = forms.ChoiceField(label='Statut', choices=Profile.STATUS_CHOICES, initial='available', required=False)
    education_level = forms.CharField(label="Niveau d'etude", max_length=120, required=False)
    location = forms.CharField(label='Localisation', max_length=120, required=False)
    phone = forms.CharField(label='Telephone', max_length=30, required=False)
    whatsapp = forms.CharField(label='WhatsApp', max_length=30, required=False)
    linkedin_url = forms.URLField(label='Lien LinkedIn', required=False)
    photo_file = forms.FileField(label='Photo de profil', required=False, validators=[validate_image_file])
    photo_url = forms.URLField(label='Lien vers une photo', required=False)
    cv_file = forms.FileField(label='CV (PDF ou DOCX)', required=False, validators=[validate_cv_file])
    is_public = forms.BooleanField(
        label='Rendre mon profil visible publiquement',
        required=False,
        initial=True,
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': "Nom d'utilisateur",
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Un compte avec cet email existe deja.')
        return email
