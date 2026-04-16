"""
API Views for the users app.

Endpoints
─────────
POST   /api/users/register/         → Create account
POST   /api/users/login/            → JWT login (access + refresh)
POST   /api/users/login/refresh/    → Refresh access token
POST   /api/users/logout/           → Blacklist refresh token
GET    /api/users/me/               → Logged-in user profile
PATCH  /api/users/me/update/        → Update own profile
POST   /api/users/me/change-password/ → Change password
GET    /api/users/                  → List all users  (admin only)
GET    /api/users/<id>/             → Get any user    (admin only)
PATCH  /api/users/<id>/             → Edit any user   (admin only)
DELETE /api/users/<id>/             → Delete user     (admin only)
"""
from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    AdminUserSerializer,
)
from .permissions import IsAdminRole

User = get_user_model()


# ─────────────────────────────────────────────────────────────
# 1. Register
# ─────────────────────────────────────────────────────────────
class RegisterView(generics.CreateAPIView):
    """
    POST /api/users/register/
    Public endpoint — no authentication required.
    """
    queryset            = User.objects.all()
    serializer_class    = RegisterSerializer
    permission_classes  = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Auto-generate tokens so the user is immediately logged in
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Account created successfully.",
                "user": UserProfileSerializer(user, context={"request": request}).data,
                "tokens": {
                    "access":  str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────
# 2. Login (JWT)
# ─────────────────────────────────────────────────────────────
class LoginView(TokenObtainPairView):
    """
    POST /api/users/login/
    Returns access + refresh tokens plus full user profile.
    Public endpoint.
    """
    serializer_class   = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


# ─────────────────────────────────────────────────────────────
# 3. Logout
# ─────────────────────────────────────────────────────────────
class LogoutView(APIView):
    """
    POST /api/users/logout/
    Body: { "refresh": "<refresh_token>" }
    Blacklists the refresh token so it can never be reused.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────────────────────
# 4. My Profile — GET / PATCH
# ─────────────────────────────────────────────────────────────
class MyProfileView(APIView):
    """
    GET   /api/users/me/         → View own profile
    PATCH /api/users/me/update/  → Update own profile
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class UpdateProfileView(generics.UpdateAPIView):
    """PATCH /api/users/me/update/"""
    serializer_class   = UpdateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names  = ["patch"]       # only PATCH, not PUT

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        response = super().update(request, *args, **kwargs)
        # Return the full updated profile
        return Response(
            {
                "message": "Profile updated successfully.",
                "user": UserProfileSerializer(request.user, context={"request": request}).data,
            }
        )


# ─────────────────────────────────────────────────────────────
# 5. Change Password
# ─────────────────────────────────────────────────────────────
class ChangePasswordView(APIView):
    """POST /api/users/me/change-password/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Password changed successfully. Please log in again."},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────
# 6. Admin — User Management
# ─────────────────────────────────────────────────────────────
class AdminUserListView(generics.ListAPIView):
    """
    GET /api/users/
    Returns paginated list of all users. Admin role only.
    """
    queryset           = User.objects.all()
    serializer_class   = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get_queryset(self):
        qs     = super().get_queryset()
        role   = self.request.query_params.get("role")
        search = self.request.query_params.get("search")
        if role:
            qs = qs.filter(role=role)
        if search:
            qs = qs.filter(email__icontains=search) | qs.filter(first_name__icontains=search)
        return qs


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/users/<id>/  → retrieve
    PATCH  /api/users/<id>/  → partial update
    DELETE /api/users/<id>/  → soft-delete (deactivate)
    Admin role only.
    """
    queryset           = User.objects.all()
    serializer_class   = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def destroy(self, request, *args, **kwargs):
        """Soft-delete: deactivate instead of removing from DB."""
        user = self.get_object()
        if user == request.user:
            return Response(
                {"error": "You cannot delete your own account via this endpoint."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False
        user.save()
        return Response({"message": f"User {user.email} has been deactivated."}, status=status.HTTP_200_OK)
