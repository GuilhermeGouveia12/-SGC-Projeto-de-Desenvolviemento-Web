from django.db import models
from django.core.validators import MinValueValidator


class Produto(models.Model):
    nome         = models.CharField(max_length=100)
    descricao    = models.TextField(blank=True, null=True)
    preco        = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    qtd_estoque  = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    estoque_min  = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    ativo        = models.BooleanField(default=True)

    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table     = 'produtos'
        ordering     = ['nome']
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return self.nome

    def estoque_suficiente(self, quantidade):
        return self.qtd_estoque >= quantidade

    def abaixo_estoque_minimo(self):
        return self.qtd_estoque <= self.estoque_min
