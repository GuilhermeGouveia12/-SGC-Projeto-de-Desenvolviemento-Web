from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.usuarios.models import Usuario
from .models import Produto


class ProdutoAPITest(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.usuario = Usuario.objects.create_user(username='testuser', password='senha123', perfil='ADMIN')
        resp = self.api.post('/auth/login', {'username': 'testuser', 'password': 'senha123'}, format='json')
        self.api.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["access"]}')

    def _payload(self, nome='Teclado', preco='150.00', qtd=10):
        return {'nome': nome, 'preco': preco, 'qtd_estoque': qtd, 'estoque_min': 2}

    def test_criar_produto(self):
        resp = self.api.post('/produtos/', self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_preco_negativo(self):
        resp = self.api.post('/produtos/', self._payload(preco='-10.00'), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_listar_produtos(self):
        Produto.objects.create(nome='Mouse', preco=50, qtd_estoque=5, estoque_min=1)
        resp = self.api.get('/produtos/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_editar_produto(self):
        p = Produto.objects.create(**{'nome': 'HD', 'preco': 200, 'qtd_estoque': 3, 'estoque_min': 1})
        resp = self.api.put(f'/produtos/{p.id}/', {**self._payload(), 'nome': 'HD Externo'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['nome'], 'HD Externo')

    def test_remover_produto(self):
        p = Produto.objects.create(nome='Cabo', preco=10, qtd_estoque=20, estoque_min=5)
        resp = self.api.delete(f'/produtos/{p.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
