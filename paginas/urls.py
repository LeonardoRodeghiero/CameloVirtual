from django.urls import path
from .views import IndexView, AcessoNegadoView, ClienteProdutoList, ProdutoEspecifico, VerCarrinho, alterar_quantidade, CameloView, AcessoNegadoCameloView, ClienteProdutoCameloList, ProdutoCameloEspecifico, ClienteCameloList
urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('<int:pk>/', CameloView.as_view(), name="camelo"),

    path('sem-permissao/', AcessoNegadoView.as_view(), name="acesso-negado"),
    path('<int:pk>/sem-permissao/', AcessoNegadoCameloView.as_view(), name="acesso-negado-camelo"),

    path('produtos/', ClienteProdutoList.as_view(), name="produtos"),
    path('camelos/', ClienteCameloList.as_view(), name="camelos"),

    path('<int:pk>/produtos/', ClienteProdutoCameloList.as_view(), name="produtos-camelo"),

    path('produto/<int:pk>/', ProdutoEspecifico.as_view(), name="produto"),
    path('<int:camelo_id>/produto/<int:produto_id>/', ProdutoCameloEspecifico.as_view(), name="produto-camelo"),

    path('carrinho/', VerCarrinho.as_view(), name='ver-carrinho'),
    path('carrinho/alterar/<int:item_id>/<str:acao>/', alterar_quantidade, name='alterar-quantidade'),

]
