"""
Register User model in Django Admin with a rich display.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering        = ["-date_joined"]
    list_display    = ["email", "get_full_name", "role", "is_active", "is_staff", "date_joined"]
    list_filter     = ["role", "is_active", "is_staff"]
    search_fields   = ["email", "first_name", "last_name"]
    readonly_fields = ["date_joined", "last_login", "updated_at"]

    fieldsets = (
        (None,                   {"fields": ("email", "password")}),
        (_("Personal Info"),     {"fields": ("first_name", "last_name", "phone", "bio", "avatar")}),
        (_("Role & Permissions"),{"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Timestamps"),        {"fields": ("date_joined", "last_login", "updated_at")}),
    )

    # Fields shown when creating a new user in the admin
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("email", "first_name", "last_name", "password1", "password2", "role"),
        }),
    )
