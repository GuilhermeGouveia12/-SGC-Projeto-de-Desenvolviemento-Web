from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cliente
from .serializers import ClienteSerializer
from sgc.exceptions import ClienteComVendasException


class ClienteListView(LoginRequiredMixin, ListView):
    model               = Cliente
    template_name       = 'clientes/lista.html'
    context_object_name = 'clientes'
    login_url           = '/web/login/'

    def get_queryset(self):
        qs   = super().get_queryset()
        nome = self.request.GET.get('nome', '')
        if nome:
            qs = qs.filter(nome__icontains=nome)
        return qs


class ClienteCreateView(LoginRequiredMixin, CreateView):
    model         = Cliente
    fields        = ['nome', 'cpf', 'email', 'telefone', 'endereco']
    template_name = 'clientes/form.html'
    success_url   = reverse_lazy('web-clientes-list')
    login_url     = '/web/login/'

    def form_valid(self, form):
        messages.success(self.request, 'Cliente cadastrado com sucesso.')
        return super().form_valid(form)


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model         = Cliente
    fields        = ['nome', 'cpf', 'email', 'telefone', 'endereco']
    template_name = 'clientes/form.html'
    success_url   = reverse_lazy('web-clientes-list')
    login_url     = '/web/login/'

    def form_valid(self, form):
        messages.success(self.request, 'Cliente atualizado com sucesso.')
        return super().form_valid(form)


class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model         = Cliente
    template_name = 'clientes/confirmar_exclusao.html'
    success_url   = reverse_lazy('web-clientes-list')
    login_url     = '/web/login/'

    def post(self, request, *args, **kwargs):
        cliente = self.get_object()
        if cliente.possui_vendas():
            messages.error(request, 'Este cliente possui vendas registradas e não pode ser removido.')
            return self.get(request, *args, **kwargs)
        messages.success(request, 'Cliente removido com sucesso.')
        return super().post(request, *args, **kwargs)
