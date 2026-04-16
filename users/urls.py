"""
URL patterns for the users app.
All paths are prefixed with /api/users/ (defined in core/urls.py).
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    MyProfileView,
    UpdateProfileView,
    ChangePasswordView,
    AdminUserListView,
    AdminUserDetailView,
)

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────
    path("register/",           RegisterView.as_view(),   name="user-register"),
    path("login/",              LoginView.as_view(),      name="user-login"),
    path("login/refresh/",      TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/",             LogoutView.as_view(),     name="user-logout"),

    # ── Logged-in user ────────────────────────────────────────
    path("me/",                 MyProfileView.as_view(),    name="user-profile"),
    path("me/update/",          UpdateProfileView.as_view(), name="user-update"),
    path("me/change-password/", ChangePasswordView.as_view(), name="change-password"),

    # ── Admin management ──────────────────────────────────────
    path("",                    AdminUserListView.as_view(),   name="admin-user-list"),
    path("<int:pk>/",           AdminUserDetailView.as_view(), name="admin-user-detail"),
]
