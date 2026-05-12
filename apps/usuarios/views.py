from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from .serializers import SGCTokenSerializer


class LoginView(TokenObtainPairView):
    """POST /auth/login — retorna access + refresh token JWT."""
    permission_classes = [AllowAny]
    serializer_class   = SGCTokenSerializer
