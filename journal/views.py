from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import Notification
from .forms import JournalPostCommentForm, JournalPostForm
from .models import JournalPost, JournalPostComment, JournalPostLike


def post_list(request):
    posts = JournalPost.objects.filter(is_published=True)
    return render(request, 'journal/post_list.html', {'posts': posts})


def post_detail(request, slug):
    post = get_object_or_404(JournalPost, slug=slug, is_published=True)
    comments = post.comments.select_related('user')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"{request.build_absolute_uri('/accounts/connexion/')}?next={request.path}")
        form = JournalPostCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            messages.success(request, 'Votre commentaire a ete enregistre.')
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
            post.save()
            form.save_m2m()
            recipients = User.objects.filter(is_active=True).exclude(pk=request.user.pk)
            notifications = [
                Notification(
                    user=user,
                    title="Nouvelle publication dans le journal",
                    message=f"Une nouvelle publication '{post.title}' est disponible.",
                    link=post.get_absolute_url(),
                    type='journal',
                )
                for user in recipients
            ]
            Notification.objects.bulk_create(notifications)
            messages.success(request, 'Publication publiee avec succes.')
            return redirect(post)
    else:
        form = JournalPostForm()

    return render(request, 'journal/post_form.html', {'form': form})


@login_required
def post_like(request, slug):
    post = get_object_or_404(JournalPost, slug=slug, is_published=True)
    like, created = JournalPostLike.objects.get_or_create(user=request.user, post=post)
    if created:
        messages.success(request, 'Vous avez aime cet article.')
    else:
        messages.info(request, 'Vous avez deja aime cet article.')
    return redirect(post)
