from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Produto


class ProdutoListView(LoginRequiredMixin, ListView):
    model               = Produto
    template_name       = 'produtos/lista.html'
    context_object_name = 'produtos'
    login_url           = '/web/login/'

    def get_queryset(self):
        qs   = super().get_queryset()
        nome = self.request.GET.get('nome', '')
        if nome:
            qs = qs.filter(nome__icontains=nome)
        return qs


class ProdutoCreateView(LoginRequiredMixin, CreateView):
    model         = Produto
    fields        = ['nome', 'descricao', 'preco', 'qtd_estoque', 'estoque_min']
    template_name = 'produtos/form.html'
    success_url   = reverse_lazy('web-produtos-list')
    login_url     = '/web/login/'

    def form_valid(self, form):
        messages.success(self.request, 'Produto cadastrado com sucesso.')
        return super().form_valid(form)


class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    model         = Produto
    fields        = ['nome', 'descricao', 'preco', 'qtd_estoque', 'estoque_min', 'ativo']
    template_name = 'produtos/form.html'
    success_url   = reverse_lazy('web-produtos-list')
    login_url     = '/web/login/'

    def form_valid(self, form):
        messages.success(self.request, 'Produto atualizado com sucesso.')
        return super().form_valid(form)


class ProdutoDeleteView(LoginRequiredMixin, DeleteView):
    model         = Produto
    template_name = 'produtos/confirmar_exclusao.html'
    success_url   = reverse_lazy('web-produtos-list')
    login_url     = '/web/login/'

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Produto removido com sucesso.')
        return super().post(request, *args, **kwargs)
