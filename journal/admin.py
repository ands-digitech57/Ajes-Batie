from django.contrib import admin
from .models import JournalPost, JournalPostLike


@admin.register(JournalPost)
class JournalPostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'category', 'is_published', 'created_at')


@admin.register(JournalPostLike)
class JournalPostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    search_fields = ('post__title', 'user__username')