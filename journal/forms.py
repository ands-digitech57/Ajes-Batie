from django import forms
from .models import JournalPost, JournalPostComment


class JournalPostForm(forms.ModelForm):
    class Meta:
        model = JournalPost
        fields = [
            'title',
            'slug',
            'summary',
            'content',
            'category',
            'event_date',
            'image_file',
            'video_file',
            'is_published',
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 6}),
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }


class JournalPostCommentForm(forms.ModelForm):
    class Meta:
        model = JournalPostComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ecrivez un commentaire...',
            }),
        }
        labels = {
            'content': 'Commentaire',
        }
