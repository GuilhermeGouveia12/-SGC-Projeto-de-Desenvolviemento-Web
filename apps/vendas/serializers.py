from rest_framework import serializers
from django.db import transaction
from .models import Venda, ItemVenda
from apps.produtos.models import Produto
from sgc.exceptions import EstoqueInsuficienteException, VendaSemItensException


class ItemVendaSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)
    subtotal     = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = ItemVenda
        fields = ['id', 'produto', 'produto_nome', 'quantidade', 'preco_unitario', 'subtotal']


class ItemVendaCreateSerializer(serializers.Serializer):
    produto_id = serializers.IntegerField()
    quantidade = serializers.IntegerField(min_value=1)


class VendaSerializer(serializers.ModelSerializer):
    itens         = ItemVendaSerializer(many=True, read_only=True)
    cliente_nome  = serializers.CharField(source='cliente.nome', read_only=True)
    usuario_nome  = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model  = Venda
        fields = ['id', 'cliente', 'cliente_nome', 'usuario', 'usuario_nome', 'data', 'valor_total', 'itens']
        read_only_fields = ['usuario', 'data', 'valor_total']


class VendaCreateSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    itens      = ItemVendaCreateSerializer(many=True)

    def validate_itens(self, itens):
        if not itens:
            raise VendaSemItensException()
        return itens

    @transaction.atomic
    def create(self, validated_data):
        from apps.clientes.models import Cliente

        cliente = Cliente.objects.get(pk=validated_data['cliente_id'])
        usuario = self.context['request'].user

        venda = Venda.objects.create(cliente=cliente, usuario=usuario)

        for item_data in validated_data['itens']:
            produto = Produto.objects.select_for_update().get(pk=item_data['produto_id'])

            if not produto.estoque_suficiente(item_data['quantidade']):
                raise EstoqueInsuficienteException(
                    f'Estoque insuficiente para "{produto.nome}". '
                    f'Disponível: {produto.qtd_estoque}, solicitado: {item_data["quantidade"]}.'
                )

            ItemVenda.objects.create(
                venda=venda,
                produto=produto,
                quantidade=item_data['quantidade'],
                preco_unitario=produto.preco,
            )

            produto.qtd_estoque -= item_data['quantidade']
            produto.save(update_fields=['qtd_estoque'])

        venda.recalcular_total()
        return venda
