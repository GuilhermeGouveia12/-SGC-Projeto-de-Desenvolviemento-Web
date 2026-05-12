from django.urls import path
from . import views_web

urlpatterns = [
    path('web/vendas/',             views_web.VendaListView.as_view(),   name='web-vendas-list'),
    path('web/vendas/nova/',        views_web.VendaCreateView.as_view(), name='web-vendas-create'),
    path('web/vendas/<int:pk>/',    views_web.VendaDetailView.as_view(), name='web-vendas-detail'),
    path('web/vendas/relatorio/',   views_web.RelatorioView.as_view(),   name='web-relatorio'),
    path('web/login/',              views_web.LoginWebView.as_view(),    name='web-login'),
    path('web/logout/',             views_web.logout_view,               name='web-logout'),
    path('web/',                    views_web.DashboardView.as_view(),   name='web-dashboard'),
]
