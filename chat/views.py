from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Message

@login_required
def inbox(request, recipient_id=None):
    user = request.user
    
    # 1. Récupérer tous les utilisateurs avec qui on a déjà discuté
    # (Soit on a envoyé, soit on a reçu un message d'eux)
    discussed_users_ids = Message.objects.filter(Q(sender=user) | Q(recipient=user)).values_list('sender_id', 'recipient_id')
    
    # On met à plat la liste des IDs et on retire notre propre ID
    flat_ids = set([item for sublist in discussed_users_ids for item in sublist if item != user.id])
    contacts = User.objects.filter(id__in=flat_ids)

    active_conversation = None
    messages = []

    # 2. Si on a sélectionné un destinataire précis (un contact)
    if recipient_id:
        active_conversation = get_object_or_404(User, id=recipient_id)
        
        # Si la personne n'était pas encore dans nos contacts, on l'ajoute dynamiquement à la liste visible à gauche
        if active_conversation not in contacts:
            contacts = list(contacts) + [active_conversation]

        # Charger l'historique complet des messages entre ces deux utilisateurs
        messages = Message.objects.filter(
            (Q(sender=user) & Q(recipient=active_conversation)) |
            (Q(sender=active_conversation) & Q(recipient=user))
        ).order_by('created_at')

        # Marquer les messages reçus comme "lus"
        Message.objects.filter(sender=active_conversation, recipient=user, is_read=False).update(is_read=True)

        # 3. Traiter l'envoi d'un nouveau message
        if request.method == 'POST':
            content = request.POST.get('content', '').strip()
            if content:
                Message.objects.create(
                    sender=user,
                    recipient=active_conversation,
                    content=content
                )
                return redirect('chat:inbox_with_user', recipient_id=recipient_id)

    return render(request, 'chat/inbox.html', {
        'contacts': contacts,
        'active_conversation': active_conversation,
        'messages': messages,
    })