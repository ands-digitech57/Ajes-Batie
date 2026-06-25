import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from accounts.models import Notification
from .forms import JournalPostCommentForm, JournalPostForm
from .models import JournalPost, JournalPostComment, JournalPostLike

def post_list(request):
    posts = JournalPost.objects.filter(is_published=True).prefetch_related('media_items')
    return render(request, 'journal/post_list.html', {'posts': posts})

def post_detail(request, slug):
    post = get_object_or_404(JournalPost, slug=slug, is_published=True)
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
            return redirect(post)
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
        return redirect('journal:list')

    if request.method == 'POST':
        form = JournalPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            # Sécurité renforcée pour le slug afin d'éviter l'Erreur 500
            if not post.slug:
                base_slug = slugify(post.title)
                if JournalPost.objects.filter(slug=base_slug).exists():
                    post.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
                else:
                    post.slug = base_slug
            
            post.save()
            form.save_m2m()
            
            # Envoi des notifications en lot (bulk)
            recipients = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
            notifications = [
                Notification(
                    user=user,
                    title="📰 Nouvelle publication dans le journal",
                    message=f"Une nouvelle publication '{post.title}' est disponible.",
                    link=post.get_absolute_url(),
                    type='journal',
                )
                for user in recipients
            ]
            Notification.objects.bulk_create(notifications)
            
            messages.success(request, 'Publication publiée avec succès.')
            return redirect(post)
    else:
        form = JournalPostForm()

    return render(request, 'journal/post_form.html', {'form': form})

@login_required
def post_like(request, slug):
    post = get_object_or_404(JournalPost, slug=slug, is_published=True)
    like, created = JournalPostLike.objects.get_or_create(user=request.user, post=post)
    if created:
        messages.success(request, 'Vous avez aimé cet article.')
    else:
        like.delete() # Un deuxième clic retire le like (comportement naturel moderne)
        messages.info(request, 'Mentions j\'aime actualisée.')
    return redirect(post)