from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'telephone', 'is_staff', 'must_change_password']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('HOUSKi', {'fields': ('telephone', 'roles', 'must_change_password')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('HOUSKi', {'fields': ('telephone', 'roles', 'must_change_password')}),
    )
