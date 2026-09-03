from django.contrib import admin
from .models import PictureOfWeek


@admin.register(PictureOfWeek)
class PictureOfWeekAdmin(admin.ModelAdmin):
    list_display = ['description', 'author', 'uploaded_at', 'is_active']
    list_editable = ['is_active']
