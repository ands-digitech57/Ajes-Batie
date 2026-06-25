from django import forms
from .models import JournalPost, JournalPostComment

class JournalPostForm(forms.ModelForm):
    class Meta:
        model = JournalPost
        fields = [
            'title',
            'summary',
            'content',
            'category',
            'event_date',
            'is_published',
        ]
        widgets = {
            'summary': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Un court résumé de la publication...',
                'style': 'width: 100%; border-radius: 8px; padding: 10px; border: 1px solid #e2e8f0;'
            }),
            'content': forms.Textarea(attrs={
                'rows': 6, 
                'placeholder': 'Contenu détaillé de votre article...',
                'style': 'width: 100%; border-radius: 8px; padding: 10px; border: 1px solid #e2e8f0;'
            }),
            'event_date': forms.DateInput(attrs={
                'type': 'date',
                'style': 'border-radius: 8px; padding: 10px; border: 1px solid #e2e8f0;'
            }),
            'category': forms.Select(attrs={
                'style': 'width: 100%; border-radius: 8px; padding: 10px; border: 1px solid #e2e8f0; background: white;'
            }),
        }
        labels = {
            'title': 'Titre de la publication',
            'summary': 'Résumé',
            'content': 'Contenu de l\'article',
            'category': 'Catégorie',
            'event_date': 'Date de l\'événement (Optionnel)',
            'is_published': 'Publier immédiatement',
        }


class JournalPostCommentForm(forms.ModelForm):
    class Meta:
        model = JournalPostComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Écrivez un commentaire...',
                'style': 'width: 100%; border-radius: 8px; padding: 12px; border: 1px solid #e2e8f0; resize: none;'
            }),
        }
        labels = {
            'content': 'Commentaire',
        }