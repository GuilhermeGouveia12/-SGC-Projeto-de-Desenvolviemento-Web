from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.usuarios.models import Usuario
from apps.clientes.models import Cliente
from apps.produtos.models import Produto
from .models import Venda


class VendaAPITest(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.usuario = Usuario.objects.create_user(username='vendedor', password='senha123', perfil='FUNCIONARIO')
        resp = self.api.post('/auth/login', {'username': 'vendedor', 'password': 'senha123'}, format='json')
        self.api.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["access"]}')

        self.cliente = Cliente.objects.create(nome='Ana', cpf='98765432100', email='ana@teste.com')
        self.produto = Produto.objects.create(nome='SSD', preco=300, qtd_estoque=10, estoque_min=2)

    def _payload(self, qtd=2):
        return {
            'cliente_id': self.cliente.id,
            'itens': [{'produto_id': self.produto.id, 'quantidade': qtd}],
        }

    def test_criar_venda(self):
        resp = self.api.post('/vendas/', self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['valor_total'], '600.00')

    def test_estoque_atualizado_apos_venda(self):
        self.api.post('/vendas/', self._payload(qtd=3), format='json')
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.qtd_estoque, 7)

    def test_estoque_insuficiente(self):
        resp = self.api.post('/vendas/', self._payload(qtd=999), format='json')
        self.assertEqual(resp.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_venda_sem_itens(self):
        payload = {'cliente_id': self.cliente.id, 'itens': []}
        resp = self.api.post('/vendas/', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_listar_vendas(self):
        resp = self.api.get('/vendas/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_filtro_por_cliente(self):
        self.api.post('/vendas/', self._payload(), format='json')
        resp = self.api.get(f'/vendas/?cliente_id={self.cliente.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)

    def test_venda_nao_pode_ser_editada(self):
        r = self.api.post('/vendas/', self._payload(), format='json')
        resp = self.api.put(f'/vendas/{r.data["id"]}/', self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
