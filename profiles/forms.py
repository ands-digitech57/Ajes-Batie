from django import forms
from .models import Profile, Skill


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Prenom', required=False)
    last_name = forms.CharField(label='Nom', required=False)
    skills_text = forms.CharField(
        label='Competences',
        required=False,
        help_text='Separez les competences par des virgules.',
        widget=forms.TextInput(attrs={'placeholder': 'Ex: informatique, couture, comptabilite'}),
    )

    class Meta:
        model = Profile
        fields = [
            'job_title',
            'current_company',
            'industry',
            'bio',
            'skills_text',
            'status',
            'education_level',
            'location',
            'phone',
            'whatsapp',
            'linkedin_url',
            'photo_url',
            'photo_file',
            'cv_file',
            'email',
            'is_public',
        ]
        labels = {
            'job_title': 'Metier ou titre',
            'current_company': 'Entreprise actuelle',
            'industry': 'Secteur',
            'bio': 'Presentation',
            'status': 'Statut',
            'education_level': "Niveau d'etude",
            'location': 'Localisation',
            'phone': 'Telephone',
            'whatsapp': 'WhatsApp',
            'linkedin_url': 'Lien LinkedIn',
            'photo_url': 'Photo (URL)',
            'photo_file': 'Photo de profil',
            'cv_file': 'CV (PDF ou DOCX)',
            'email': 'Email',
            'is_public': 'Rendre mon profil visible publiquement',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
            'photo_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'photo_file': forms.ClearableFileInput(),
            'cv_file': forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['skills_text'].initial = ', '.join(
                self.instance.skills.values_list('name', flat=True)
            )
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        from django.db import transaction

        profile = super().save(commit=False)
        profile.user.first_name = self.cleaned_data.get('first_name', profile.user.first_name)
        profile.user.last_name = self.cleaned_data.get('last_name', profile.user.last_name)
        if commit:
            with transaction.atomic():
                profile.user.save()
                profile.save()
                skills_text = self.cleaned_data.get('skills_text', '')
                names = [item.strip().lower() for item in skills_text.split(',') if item.strip()]
                skills = []
                for name in names:
                    skill, _ = Skill.objects.get_or_create(name=name)
                    skills.append(skill)
                profile.skills.set(skills)
        else:
            profile._pending_skills = self.cleaned_data.get('skills_text', '')
        return profile

    def save_m2m(self):
        super().save_m2m()
        if hasattr(self, '_pending_skills'):
            skills_text = self._pending_skills
            names = [item.strip().lower() for item in skills_text.split(',') if item.strip()]
            skills = []
            for name in names:
                skill, _ = Skill.objects.get_or_create(name=name)
                skills.append(skill)
            self.instance.skills.set(skills)
