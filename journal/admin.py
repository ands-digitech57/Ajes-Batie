from django.contrib import admin
from .models import JournalPost, JournalPostMedia, JournalPostLike, JournalPostComment

class JournalPostMediaInline(admin.TabularInline):
    model = JournalPostMedia
    extra = 3  # Te donne 3 cases par défaut pour ajouter des photos/vidéos d'un coup

@admin.register(JournalPost)
class JournalPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'event_date', 'is_published')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [JournalPostMediaInline]  # Lie le système multi-images/vidéos au post

admin.site.register(JournalPostLike)
admin.site.register(JournalPostComment)