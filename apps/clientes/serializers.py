from rest_framework import serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Cliente
        fields = ['id', 'nome', 'cpf', 'email', 'telefone', 'endereco']

    def validate_cpf(self, value):
        value = value.strip()
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError('CPF deve conter exatamente 11 dígitos numéricos.')
        # unicidade excluindo o próprio objeto em edições
        qs = Cliente.objects.filter(cpf=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Já existe um cliente cadastrado com este CPF.')
        return value
