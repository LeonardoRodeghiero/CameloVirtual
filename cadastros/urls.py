from django.urls import path

from .views import CategoriaCreate, ProdutoCreate, CarrinhoCreate, CarrinhoProdutoCreate, CameloCreate

from .views import CategoriaUpdate, ProdutoUpdate

from .views import CategoriaDelete, ProdutoDelete, CarrinhoDelete, CarrinhoDeleteUser, CameloDelete

from .views import CategoriaList, PerfilList, ProdutoList, CarrinhoList, CameloList

urlpatterns = [
    
    path('cadastrar/categoria/', CategoriaCreate.as_view(), name="cadastrar-categoria"),
    path('cadastrar/produto/', ProdutoCreate.as_view(), name="cadastrar-produto"),
    path('cadastrar/camelo/', CameloCreate.as_view(), name="cadastrar-camelo"),
    path('carrinho/<int:produto_id>/', CarrinhoCreate.as_view(), name="adicionar-ao-carrinho"),
    path('carrinho/adicionar/<int:produto_id>/', CarrinhoProdutoCreate.as_view(), name="adicionar-produto-carrinho"),

    path('atualizar/categoria/<int:pk>', CategoriaUpdate.as_view(), name="atualizar-categoria"),
    path('atualizar/produto/<int:pk>/', ProdutoUpdate.as_view(), name="atualizar-produto"),

    path('excluir/categoria/<int:pk>/', CategoriaDelete.as_view(), name="excluir-categoria"),
    path('excluir/produto/<int:pk>/', ProdutoDelete.as_view(), name="excluir-produto"),
    path('excluir/carrinho/<int:pk>/', CarrinhoDelete.as_view(), name="excluir-carrinho"),
    path('excluir/carrinho/usuario/<int:pk>/', CarrinhoDeleteUser.as_view(), name="excluir-carrinho-usuario"),
    path('excluir/camelo/<int:pk>/', CameloDelete.as_view(), name="excluir-camelo"),

    path('listar/categorias/', CategoriaList.as_view(), name="listar-categorias"),
    path('listar/usuarios/', PerfilList.as_view(), name="listar-usuarios"),
    path('listar/produtos/', ProdutoList.as_view(), name="listar-produtos"),
    path('listar/carrinhos/', CarrinhoList.as_view(), name="listar-carrinhos"),
    path('listar/camelos/', CameloList.as_view(), name="listar-camelos"),

]