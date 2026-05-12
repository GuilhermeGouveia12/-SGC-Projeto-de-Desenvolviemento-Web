from rest_framework import serializers
from .models import Produto


class ProdutoSerializer(serializers.ModelSerializer):
    abaixo_estoque_minimo = serializers.SerializerMethodField()

    class Meta:
        model  = Produto
        fields = ['id', 'nome', 'descricao', 'preco', 'qtd_estoque', 'estoque_min', 'ativo', 'abaixo_estoque_minimo']

    def get_abaixo_estoque_minimo(self, obj):
        return obj.abaixo_estoque_minimo()

    def validate_preco(self, value):
        if value < 0:
            raise serializers.ValidationError('O preço não pode ser negativo.')
        return value

    def validate_qtd_estoque(self, value):
        if value < 0:
            raise serializers.ValidationError('A quantidade em estoque não pode ser negativa.')
        return value
