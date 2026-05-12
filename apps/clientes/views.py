from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cliente
from .serializers import ClienteSerializer
from sgc.exceptions import ClienteComVendasException


class ClienteViewSet(viewsets.ModelViewSet):
    queryset           = Cliente.objects.all()
    serializer_class   = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs   = super().get_queryset()
        nome = self.request.query_params.get('nome')
        cpf  = self.request.query_params.get('cpf')
        if nome:
            qs = qs.filter(nome__icontains=nome)
        if cpf:
            qs = qs.filter(cpf=cpf)
        return qs

    def destroy(self, request, *args, **kwargs):
        cliente = self.get_object()
        if cliente.possui_vendas():
            raise ClienteComVendasException()
        return super().destroy(request, *args, **kwargs)
