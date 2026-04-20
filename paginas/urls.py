from django.urls import path
from .views import IndexView, AcessoNegadoView, ClienteProdutoList, ProdutoEspecifico, VerCarrinho, alterar_quantidade, CameloView, AcessoNegadoCameloView, ClienteProdutoCameloList, ProdutoCameloEspecifico, ClienteCameloList, InserirFuncionarioView, ConfirmarFuncionarioView, ConfirmarEndereco, VerHistoricoPedidos, ProdutoCameloCategoriaList, FinalizarPedidoView, CancelarPedidoView, AvaliacoesCamelo
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

    path('<int:pk>/inserir/funcionario/', InserirFuncionarioView.as_view(), name='inserir-funcionario'),
    path("<int:pk>/confirmar/funcionario/<int:perfil_pk>/", ConfirmarFuncionarioView.as_view(), name="confirmar-funcionario"),

    path("confirmar-endereco/", ConfirmarEndereco.as_view(), name="confirmar-endereco"),

    path("historico/pedidos/", VerHistoricoPedidos.as_view(), name="historico-pedidos"),

    path("<int:camelo_id>/categoria/", ProdutoCameloCategoriaList.as_view() , name="produtos-categoria"),

    path('pedido/finalizar/<int:pk>/', FinalizarPedidoView.as_view(), name='finalizar-pedido'),

    path('pedido/cancelar/<int:pk>/', CancelarPedidoView.as_view(), name='cancelar-pedido'),

    path('<int:pk>/avaliacoes', AvaliacoesCamelo.as_view(), name='todas-avaliacoes-camelo'),




]
