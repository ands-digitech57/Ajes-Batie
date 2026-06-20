from django import forms
from .models import Application, JobOffer


class JobOfferForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        exclude = ("createed_at",)

        fields = [
            'title',
            'description',
            'company_name',
            'recruiter_name',
            'recruiter_phone',
            'recruiter_email',
            'location',
            'contract_type',
            'required_skills',
            'deadline',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'required_skills': forms.Textarea(attrs={'rows': 3}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'title': "Titre de l'offre",
            'description': 'Description',
            'company_name': 'Entreprise ou activite',
            'recruiter_name': 'Nom du recruteur',
            'recruiter_phone': 'Telephone ou WhatsApp',
            'recruiter_email': 'Email du recruteur',
            'location': 'Lieu',
            'contract_type': 'Type de contrat',
            'required_skills': 'Competences demandees',
            'deadline': 'Date limite',
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['message']
        labels = {
            'message': 'Message au recruteur',
        }
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Presentez rapidement votre motivation, votre disponibilite ou votre experience.',
            }),
        }
