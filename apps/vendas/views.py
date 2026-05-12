from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from .models import Venda
from .serializers import VendaSerializer, VendaCreateSerializer


class VendaViewSet(viewsets.ModelViewSet):
    queryset           = Venda.objects.select_related('cliente', 'usuario').prefetch_related('itens__produto')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return VendaCreateSerializer
        return VendaSerializer

    def get_queryset(self):
        qs         = super().get_queryset()
        cliente_id = self.request.query_params.get('cliente_id')
        data_ini   = self.request.query_params.get('data_inicio')
        data_fim   = self.request.query_params.get('data_fim')

        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)
        if data_ini:
            qs = qs.filter(data__date__gte=data_ini)
        if data_fim:
            qs = qs.filter(data__date__lte=data_fim)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = VendaCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        venda = serializer.save()
        return Response(VendaSerializer(venda).data, status=status.HTTP_201_CREATED)

    # bloqueia edição e remoção de vendas
    def update(self, request, *args, **kwargs):
        return Response({'erro': 'Vendas não podem ser editadas.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({'erro': 'Vendas não podem ser removidas.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['get'], url_path='relatorio/periodo')
    def relatorio_periodo(self, request):
        """GET /vendas/relatorio/periodo/?data_inicio=AAAA-MM-DD&data_fim=AAAA-MM-DD"""
        qs = self.get_queryset()
        total   = qs.aggregate(total=Sum('valor_total'), quantidade=Count('id'))
        vendas  = VendaSerializer(qs, many=True).data
        return Response({
            'total_vendas':  total['quantidade'] or 0,
            'valor_total':   total['total'] or 0,
            'vendas':        vendas,
        })

    @action(detail=False, methods=['get'], url_path='relatorio/mensal')
    def relatorio_mensal(self, request):
        """GET /vendas/relatorio/mensal/ — agrupa vendas por mês para gráfico anual."""
        ano = self.request.query_params.get('ano')
        qs  = Venda.objects.all()
        if ano:
            qs = qs.filter(data__year=ano)

        dados = (
            qs
            .annotate(mes=TruncMonth('data'))
            .values('mes')
            .annotate(total=Sum('valor_total'), quantidade=Count('id'))
            .order_by('mes')
        )
        return Response(list(dados))
