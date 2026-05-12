from django.views.generic import ListView, DetailView, View, TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json

from .models import Venda
from apps.clientes.models import Cliente
from apps.produtos.models import Produto


LOGIN_URL = '/web/login/'


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'base/dashboard.html'
    login_url     = LOGIN_URL

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_clientes'] = Cliente.objects.count()
        ctx['total_produtos'] = Produto.objects.filter(ativo=True).count()
        ctx['total_vendas']   = Venda.objects.count()
        ctx['faturamento']    = Venda.objects.aggregate(t=Sum('valor_total'))['t'] or 0
        ctx['estoque_baixo']  = Produto.objects.filter(qtd_estoque__lte=0).count()
        return ctx


class VendaListView(LoginRequiredMixin, ListView):
    model               = Venda
    template_name       = 'vendas/lista.html'
    context_object_name = 'vendas'
    login_url           = LOGIN_URL

    def get_queryset(self):
        qs       = super().get_queryset().select_related('cliente', 'usuario')
        data_ini = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        cliente  = self.request.GET.get('cliente_id')
        if data_ini:
            qs = qs.filter(data__date__gte=data_ini)
        if data_fim:
            qs = qs.filter(data__date__lte=data_fim)
        if cliente:
            qs = qs.filter(cliente_id=cliente)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['clientes'] = Cliente.objects.all()
        return ctx


class VendaDetailView(LoginRequiredMixin, DetailView):
    model               = Venda
    template_name       = 'vendas/detalhe.html'
    context_object_name = 'venda'
    login_url           = LOGIN_URL

    def get_queryset(self):
        return super().get_queryset().prefetch_related('itens__produto')


class VendaCreateView(LoginRequiredMixin, View):
    template_name = 'vendas/form.html'
    login_url     = LOGIN_URL

    def get(self, request):
        return render(request, self.template_name, {
            'clientes': Cliente.objects.all(),
            'produtos': Produto.objects.filter(ativo=True, qtd_estoque__gt=0),
        })

    def post(self, request):
        from apps.vendas.serializers import VendaCreateSerializer
        from sgc.exceptions import EstoqueInsuficienteException, VendaSemItensException

        itens_raw = request.POST.getlist('produto_id[]')
        qtds_raw  = request.POST.getlist('quantidade[]')

        itens = []
        for pid, qty in zip(itens_raw, qtds_raw):
            try:
                itens.append({'produto_id': int(pid), 'quantidade': int(qty)})
            except (ValueError, TypeError):
                pass

        data = {'cliente_id': request.POST.get('cliente_id'), 'itens': itens}

        class FakeRequest:
            user = request.user

        serializer = VendaCreateSerializer(data=data, context={'request': FakeRequest()})
        try:
            if serializer.is_valid():
                serializer.save()
                messages.success(request, 'Venda registrada com sucesso.')
                return redirect('web-vendas-list')
            else:
                messages.error(request, 'Dados inválidos. Verifique os campos.')
        except (EstoqueInsuficienteException, VendaSemItensException) as e:
            messages.error(request, e.message)

        return render(request, self.template_name, {
            'clientes': Cliente.objects.all(),
            'produtos': Produto.objects.filter(ativo=True, qtd_estoque__gt=0),
        })


class RelatorioView(LoginRequiredMixin, TemplateView):
    template_name = 'vendas/relatorio.html'
    login_url     = LOGIN_URL

    def get_context_data(self, **kwargs):
        ctx      = super().get_context_data(**kwargs)
        ano      = self.request.GET.get('ano', timezone.now().year)
        data_ini = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        cliente  = self.request.GET.get('cliente_id')

        qs = Venda.objects.filter(data__year=ano)
        if data_ini:
            qs = qs.filter(data__date__gte=data_ini)
        if data_fim:
            qs = qs.filter(data__date__lte=data_fim)
        if cliente:
            qs = qs.filter(cliente_id=cliente)

        mensal = (
            qs.annotate(mes=TruncMonth('data'))
            .values('mes')
            .annotate(total=Sum('valor_total'), qtd=Count('id'))
            .order_by('mes')
        )

        labels  = [str(m['mes'].strftime('%b/%Y')) if m['mes'] else '' for m in mensal]
        valores = [float(m['total'] or 0) for m in mensal]

        ctx['clientes']      = Cliente.objects.all()
        ctx['vendas']        = qs.select_related('cliente', 'usuario')
        ctx['total_valor']   = qs.aggregate(t=Sum('valor_total'))['t'] or 0
        ctx['total_qtd']     = qs.count()
        ctx['grafico_labels']  = json.dumps(labels)
        ctx['grafico_valores'] = json.dumps(valores)
        ctx['ano']           = ano
        return ctx


class LoginWebView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('web-dashboard')
        return render(request, 'auth/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user     = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'web-dashboard'))
        messages.error(request, 'Usuário ou senha inválidos.')
        return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('web-login')
