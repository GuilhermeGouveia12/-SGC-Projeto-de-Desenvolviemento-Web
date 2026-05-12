from django.db import models
from django.core.validators import RegexValidator, EmailValidator


class Cliente(models.Model):
    nome      = models.CharField(max_length=100)
    cpf       = models.CharField(
        max_length=11, unique=True,
        validators=[RegexValidator(r'^\d{11}$', 'CPF deve conter exatamente 11 dígitos numéricos.')]
    )
    email     = models.CharField(max_length=100, validators=[EmailValidator()])
    telefone  = models.CharField(max_length=20, blank=True, null=True)
    endereco  = models.TextField(blank=True, null=True)

    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table     = 'clientes'
        ordering     = ['nome']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f'{self.nome} ({self.cpf})'

    def possui_vendas(self):
        return self.vendas.exists()
