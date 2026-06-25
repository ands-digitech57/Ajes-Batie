import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.db import IntegrityError

from accounts.models import Notification
from .forms import JournalPostCommentForm, JournalPostForm
from .models import JournalPost, JournalPostComment, JournalPostLike

def post_list(request):
    """Affiche la liste de toutes les publications publiées."""
    posts = JournalPost.objects.filter(is_published=True).prefetch_related('media_items')
    return render(request, 'journal/post_list.html', {'posts': posts})

def post_detail(request, slug):
    """Affiche les détails d'une publication et gère les commentaires."""
    post = get_object_or_404(JournalPost, slug=slug)
    comments = post.comments.select_related('user')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"/accounts/connexion/?next={request.path}")
        
        form = JournalPostCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, 'Votre commentaire a été enregistré avec succès.')
            # CORRECTION : Redirection par URL explicite pour éviter les blocages de reverse
            return redirect(f'/journal/{post.slug}/')
        else:
            messages.error(request, "Impossible d'enregistrer le commentaire. Veuillez vérifier le texte.")
    else:
        form = JournalPostCommentForm()

    return render(request, 'journal/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })

@login_required
def post_create(request):
    """Gère la création sécurisée d'un nouvel article par l'administration."""
    if not request.user.is_staff:
        messages.error(request, "Vous n'êtes pas autorisé à publier un article.")
        return redirect('/journal/')

    if request.method == 'POST':
        form = JournalPostForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                
                # Génération d'un slug unique pour l'URL
                base_slug = slugify(post.title)
                if not base_slug:
                    base_slug = "publication"
                
                slug = base_slug
                while JournalPost.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
                
                post.slug = slug
                post.save()
                
                # Sauvegarde des relations Many-to-Many et fichiers
                form.save_m2m()
                
                # Système de notification isolé
                try:
                    recipients = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
                    notifications = [
                        Notification(
                            user=user,
                            title="📰 Nouvelle publication",
                            message=f"L'article '{post.title}' a été publié dans le journal.",
                            link=f"/journal/{post.slug}/",
                        )
                        for user in recipients
                    ]
                    Notification.objects.bulk_create(notifications)
                except Exception:
                    pass 
                
                messages.success(request, 'Félicitations ! Votre article a été publié avec succès.')
                return redirect('/journal/')

            except IntegrityError as e:
                messages.error(request, f"Erreur de contrainte de la base de données : {str(e)}")
            except Exception as e:
                messages.error(request, f"Erreur critique lors de la sauvegarde : {str(e)}")
        else:
            # Traitement explicite et affichage des erreurs de validation
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Champ [{field}] : {error}")
    else:
        form = JournalPostForm()

    return render(request, 'journal/post_form.html', {'form': form})

@login_required
def post_like(request, slug):
    """Gère l'ajout et le retrait des mentions J'aime."""
    post = get_object_or_404(JournalPost, slug=slug)
    like, created = JournalPostLike.objects.get_or_create(user=request.user, post=post)
    
    if created:
        messages.success(request, 'Vous aimez cette publication.')
    else:
        like.delete()
        messages.info(request, 'Mention J\'aime retirée.')
        
    return redirect('/journal/')