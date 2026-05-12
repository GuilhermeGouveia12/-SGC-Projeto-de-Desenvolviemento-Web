from django.urls import path
from . import views_web

urlpatterns = [
    path('web/produtos/',                    views_web.ProdutoListView.as_view(),   name='web-produtos-list'),
    path('web/produtos/novo/',               views_web.ProdutoCreateView.as_view(), name='web-produtos-create'),
    path('web/produtos/<int:pk>/editar/',    views_web.ProdutoUpdateView.as_view(), name='web-produtos-edit'),
    path('web/produtos/<int:pk>/excluir/',   views_web.ProdutoDeleteView.as_view(), name='web-produtos-delete'),
]
