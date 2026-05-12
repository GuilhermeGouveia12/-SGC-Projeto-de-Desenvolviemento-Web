from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.usuarios.models import Usuario
from .models import Cliente


class ClienteAPITest(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.usuario = Usuario.objects.create_user(username='testuser', password='senha123', perfil='ADMIN')
        resp = self.client_api.post('/auth/login', {'username': 'testuser', 'password': 'senha123'}, format='json')
        self.token = resp.data['access']
        self.client_api.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def _payload(self, cpf='12345678901'):
        return {'nome': 'João Teste', 'cpf': cpf, 'email': 'joao@teste.com', 'telefone': '61999999999'}

    def test_criar_cliente(self):
        resp = self.client_api.post('/clientes/', self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cliente.objects.count(), 1)

    def test_cpf_duplicado(self):
        self.client_api.post('/clientes/', self._payload(), format='json')
        resp = self.client_api.post('/clientes/', self._payload(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cpf_invalido(self):
        payload = self._payload(cpf='123')
        resp = self.client_api.post('/clientes/', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_listar_clientes(self):
        Cliente.objects.create(nome='Maria', cpf='11122233344', email='maria@teste.com')
        resp = self.client_api.get('/clientes/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_editar_cliente(self):
        c = Cliente.objects.create(**self._payload())
        resp = self.client_api.put(f'/clientes/{c.id}/', {**self._payload(), 'nome': 'João Editado'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['nome'], 'João Editado')

    def test_remover_cliente_sem_vendas(self):
        c = Cliente.objects.create(**self._payload())
        resp = self.client_api.delete(f'/clientes/{c.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_sem_autenticacao(self):
        self.client_api.credentials()
        resp = self.client_api.get('/clientes/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
