from django.contrib import admin
from .models import BoardPost, BoardImage


class BoardImageInline(admin.TabularInline):
    model = BoardImage
    extra = 0


@admin.register(BoardPost)
class BoardPostAdmin(admin.ModelAdmin):
    list_display = ['headline', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['headline', 'text', 'author__username']
    date_hierarchy = 'created_at'
    inlines = [BoardImageInline]
