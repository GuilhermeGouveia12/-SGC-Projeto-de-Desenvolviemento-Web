from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from .models import Produto
from .serializers import ProdutoSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset           = Produto.objects.all()
    serializer_class   = ProdutoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs   = super().get_queryset()
        nome = self.request.query_params.get('nome')
        if nome:
            qs = qs.filter(nome__icontains=nome)
        apenas_ativos = self.request.query_params.get('ativo')
        if apenas_ativos is not None:
            qs = qs.filter(ativo=apenas_ativos.lower() == 'true')
        return qs

    @action(detail=False, methods=['get'], url_path='estoque-baixo')
    def estoque_baixo(self, request):
        """GET /produtos/estoque-baixo/ — lista produtos abaixo do estoque mínimo."""
        qs = self.get_queryset().filter(qtd_estoque__lte=F('estoque_min'))
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
