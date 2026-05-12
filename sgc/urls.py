from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from apps.usuarios.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # autenticação
    path('auth/login',   LoginView.as_view(),   name='login'),
    path('auth/refresh', TokenRefreshView.as_view(), name='token_refresh'),

    # API REST
    path('clientes/', include('apps.clientes.urls')),
    path('produtos/',  include('apps.produtos.urls')),
    path('vendas/',    include('apps.vendas.urls')),

    # interface web
    path('', include('apps.clientes.urls_web')),
    path('', include('apps.produtos.urls_web')),
    path('', include('apps.vendas.urls_web')),
]
