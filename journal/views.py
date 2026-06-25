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
    posts = JournalPost.objects.filter(is_published=True).prefetch_related('media_items')
    return render(request, 'journal/post_list.html', {'posts': posts})

def post_detail(request, slug):
    # Sécurité : on cherche le post, peu importe s'il est publié ou non pour l'auteur
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
            messages.success(request, 'Votre commentaire a été enregistré.')
            return redirect('journal:detail', slug=post.slug)
    else:
        form = JournalPostCommentForm()

    return render(request, 'journal/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })

@login_required
def post_create(request):
    if not request.user.is_staff:
        messages.error(request, "Vous n'êtes pas autorisé à publier un article.")
        return redirect('journal:post_list') # Modifié pour correspondre aux standards d'URLs

    if request.method == 'POST':
        form = JournalPostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                
                # Unification et sécurisation de la génération du slug unique
                base_slug = slugify(post.title)
                if not base_slug:
                    base_slug = "publication"
                
                # Boucle de sécurité pour s'assurer que le slug est 100% unique en BDD
                slug = base_slug
                while JournalPost.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{uuid.uuid4().hex[:4]}"
                
                post.slug = slug
                post.save()
                form.save_m2m()
                
                # Notification de la communauté isolée dans un try/except pour bloquer toute 500
                try:
                    recipients = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
                    notifications = [
                        Notification(
                            user=user,
                            title="📰 Nouvelle publication",
                            message=f"L'article '{post.title}' a été publié.",
                            link=post.get_absolute_url() if hasattr(post, 'get_absolute_url') else f"/journal/{post.slug}/",
                        )
                        for user in recipients
                    ]
                    Notification.objects.bulk_create(notifications)
                except Exception:
                    pass # Si les notifications échouent, l'article est quand même créé !
                
                messages.success(request, 'Publication publiée avec succès.')
                return redirect('journal:post_list')

            except IntegrityError as e:
                messages.error(request, f"Erreur d'intégrité de la base de données : {str(e)}")
            except Exception as e:
                messages.error(request, f"Une erreur imprévue est survenue : {str(e)}")
    else:
        form = JournalPostForm()

    return render(request, 'journal/post_form.html', {'form': form})

@login_required
def post_like(request, slug):
    post = get_object_or_404(JournalPost, slug=slug)
    like, created = JournalPostLike.objects.get_or_create(user=request.user, post=post)
    if created:
        messages.success(request, 'Vous avez aimé cet article.')
    else:
        like.delete()
        messages.info(request, 'Mention j\'aime actualisée.')
    return redirect('journal:detail', slug=post.slug)