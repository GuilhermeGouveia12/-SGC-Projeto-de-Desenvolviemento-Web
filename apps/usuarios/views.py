from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import SGCTokenSerializer


class LoginView(TokenObtainPairView):
    """POST /auth/login — retorna access + refresh token JWT."""
    permission_classes = [AllowAny]
    serializer_class   = SGCTokenSerializer


class TokenSessaoView(APIView):
    """GET /auth/token-sessao/ — emite um access token JWT para o usuário
    já autenticado por sessão. Permite que a interface web consuma a API
    REST enviando o cabeçalho Authorization: Bearer <token>."""
    authentication_classes = [SessionAuthentication]
    permission_classes     = [IsAuthenticated]

    def get(self, request):
        refresh = RefreshToken.for_user(request.user)
        return Response({'access': str(refresh.access_token)})
