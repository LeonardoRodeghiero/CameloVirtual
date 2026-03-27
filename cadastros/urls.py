from django.urls import path

from .views import CategoriaCreate, ProdutoCreate, CarrinhoCreate, CarrinhoProdutoCreate, CameloCreate, PedidoCarrinho, PedidoProdutoDireto

from .views import CategoriaUpdate, ProdutoUpdate

from .views import CategoriaDelete, ProdutoDelete, CarrinhoDelete, CarrinhoDeleteUser, CameloDelete, AvaliacaoDelete, AvaliacaoDeleteUser, PedidoDelete, PedidoDeleteUser

from .views import CategoriaList, PerfilList, ProdutoList, CarrinhoList, CameloList, CategoriaCameloList, ProdutoCameloList, AvaliacaoList, PedidoList, VerPedidosCamelo


from .views import CameloCreateWizard
from .forms import (
    CameloIdentificacaoForm,
    CameloContatoForm,
    CameloPerfilForm,
    CameloEnderecoForm,
)

from .views import ProdutoCreateWizard
from .forms import (
    ProdutoInformacaoForm,
    ProdutoDetalhesForm,
    ProdutoImagemForm,
    ProdutoFornecedorForm,
)



urlpatterns = [
    
    path('<int:pk>/cadastrar/categoria/', CategoriaCreate.as_view(), name="cadastrar-categoria"),

    path('<int:pk>/cadastrar/produto/', ProdutoCreateWizard.as_view([
        ProdutoInformacaoForm,
        ProdutoDetalhesForm,
        ProdutoImagemForm,
        ProdutoFornecedorForm,
    ]), name="cadastrar-produto"),
    path('cadastrar/camelo/', CameloCreateWizard.as_view([
        CameloIdentificacaoForm,
        CameloContatoForm,
        CameloPerfilForm,
        CameloEnderecoForm,
    ]), name="cadastrar-camelo"),
    path('carrinho/<int:produto_id>/', CarrinhoCreate.as_view(), name="adicionar-ao-carrinho"),
    path('carrinho/adicionar/<int:produto_id>/', CarrinhoProdutoCreate.as_view(), name="adicionar-produto-carrinho"),

    path('carrinho/finalizar/<int:produto_id>', PedidoCarrinho.as_view(), name="realizar-pedido-carrinho"),
    path('realizar/pedido/<int:produto_id>', PedidoProdutoDireto.as_view(), name="realizar-pedido-direto"),


    path('atualizar/categoria/<int:pk>', CategoriaUpdate.as_view(), name="atualizar-categoria"),
    path('atualizar/produto/<int:pk>/', ProdutoUpdate.as_view(), name="atualizar-produto"),

    path('excluir/categoria/<int:pk>/', CategoriaDelete.as_view(), name="excluir-categoria"),
    path('excluir/produto/<int:pk>/', ProdutoDelete.as_view(), name="excluir-produto"),
    path('excluir/carrinho/<int:pk>/', CarrinhoDelete.as_view(), name="excluir-carrinho"),
    path('excluir/carrinho/usuario/<int:pk>/', CarrinhoDeleteUser.as_view(), name="excluir-carrinho-usuario"),
    path('excluir/camelo/<int:pk>/', CameloDelete.as_view(), name="excluir-camelo"),
    path('excluir/avaliacao/<int:pk>/', AvaliacaoDelete.as_view(), name="excluir-avaliacao"),
    path('excluir/avaliacao/usuario/<int:pk>/', AvaliacaoDeleteUser.as_view(), name="excluir-avaliacao-usuario"),
    path('excluir/pedido/<int:pk>/', PedidoDelete.as_view(), name="excluir-pedido"),
    path('excluir/pedido/usuario/<int:pk>/', PedidoDeleteUser.as_view(), name="excluir-pedido-usuario"),


    path('listar/categorias/', CategoriaList.as_view(), name="listar-categorias"),
    path('<int:pk>/listar/categorias/', CategoriaCameloList.as_view(), name="listar-categorias-camelo"),

    path('listar/usuarios/', PerfilList.as_view(), name="listar-usuarios"),
    path('listar/produtos/', ProdutoList.as_view(), name="listar-produtos"),
    path('<int:pk>/listar/produtos/', ProdutoCameloList.as_view(), name="listar-produtos-camelo"),

    path('listar/carrinhos/', CarrinhoList.as_view(), name="listar-carrinhos"),
    path('listar/camelos/', CameloList.as_view(), name="listar-camelos"),
    
    path('listar/avaliacoes/', AvaliacaoList.as_view(), name="listar-avaliacoes"),
    path('listar/pedidos/', PedidoList.as_view(), name="listar-pedidos"),

    path("<int:camelo_id>/ver/pedidos/", VerPedidosCamelo.as_view(), name="listar-pedidos-camelo"),



]