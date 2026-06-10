from accounts.models import Notification
from jobs.models import JobOffer
from journal.models import JournalPost


def notifications(request):
    if not request.user.is_authenticated:
        return {}

    last_login = request.user.last_login
    if not last_login:
        return {
            'new_jobs_count': 0,
            'new_posts_count': 0,
            'unread_notifications_count': Notification.objects.filter(user=request.user, is_read=False).count(),
        }

    new_jobs_count = JobOffer.objects.filter(is_active=True, created_at__gt=last_login).count()
    new_posts_count = JournalPost.objects.filter(is_published=True, created_at__gt=last_login).count()
    unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {
        'new_jobs_count': new_jobs_count,
        'new_posts_count': new_posts_count,
        'unread_notifications_count': unread_notifications_count,
    }
