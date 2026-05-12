from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Venda(models.Model):
    cliente     = models.ForeignKey('clientes.Cliente', on_delete=models.PROTECT, related_name='vendas')
    usuario     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='vendas')
    data        = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendas'
        ordering = ['-data']
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'

    def __str__(self):
        return f'Venda #{self.id} — {self.cliente.nome}'

    def recalcular_total(self):
        from django.db.models import Sum, F, ExpressionWrapper, DecimalField
        total = self.itens.aggregate(
            total=Sum(
                ExpressionWrapper(F('quantidade') * F('preco_unitario'), output_field=DecimalField())
            )
        )['total'] or 0
        self.valor_total = total
        self.save(update_fields=['valor_total'])


class ItemVenda(models.Model):
    venda          = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto        = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT, related_name='itens_venda')
    quantidade     = models.IntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'itens_venda'
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome}'

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario
