from django.contrib import admin
from .models import Category, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['headline', 'author', 'created_at']
    list_filter = ['categories', 'created_at']
    search_fields = ['headline', 'text', 'author__username']
    date_hierarchy = 'created_at'
