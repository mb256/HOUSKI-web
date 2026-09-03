from django.contrib import admin
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'location', 'author']
    list_filter = ['start_date']
    search_fields = ['name', 'location', 'description', 'author__username']
    date_hierarchy = 'start_date'
