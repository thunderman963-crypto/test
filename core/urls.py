"""
Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(request):
    """Simple health check endpoint — Railway uses this to verify the app is up."""
    return JsonResponse({"status": "ok", "message": "Django User API is running 🚀"})


urlpatterns = [
    # Health-check (no auth required)
    path("", health_check, name="health-check"),
    path("health/", health_check, name="health-check-alt"),

    # Django Admin
    path("admin/", admin.site.urls),

    # Users API  →  /api/users/
    path("api/users/", include("users.urls")),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
