from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('compte/', include('accounts.urls')),
    path('profils/', include('profiles.urls')),
    path('offres/', include('jobs.urls')),
    path('journal/', include('journal.urls')),
    
    # MODIFIEZ CETTE LIGNE ICI :
    path('messages/', include('chat.urls', namespace='chat')),
]

if settings.DEBUG or not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)