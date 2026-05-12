from django.urls import path
from . import views_web

urlpatterns = [
    path('web/clientes/',              views_web.ClienteListView.as_view(),   name='web-clientes-list'),
    path('web/clientes/novo/',         views_web.ClienteCreateView.as_view(), name='web-clientes-create'),
    path('web/clientes/<int:pk>/editar/', views_web.ClienteUpdateView.as_view(), name='web-clientes-edit'),
    path('web/clientes/<int:pk>/excluir/', views_web.ClienteDeleteView.as_view(), name='web-clientes-delete'),
]
