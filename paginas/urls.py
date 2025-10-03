from django.urls import path
from .views import IndexView, AcessoNegadoView, ClienteProdutoList, ProdutoEspecifico, VerCarrinho, alterar_quantidade
urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('sem-permissao/', AcessoNegadoView.as_view(), name="acesso-negado"),
    path('produtos/', ClienteProdutoList.as_view(), name="produtos"),
    path('produto/<int:pk>/', ProdutoEspecifico.as_view(), name="produto"),
    path('carrinho/', VerCarrinho.as_view(), name='ver-carrinho'),
    path('carrinho/alterar/<int:item_id>/<str:acao>/', alterar_quantidade, name='alterar-quantidade'),

]
