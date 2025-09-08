from django.urls import path

from .views import CategoriaCreate, ProdutoCreate

from .views import CategoriaUpdate, ProdutoUpdate

from .views import CategoriaList, PerfilList, ProdutoList

urlpatterns = [
    
    path('cadastrar/categoria/', CategoriaCreate.as_view(), name="cadastrar-categoria"),
    path('cadastrar/produto/', ProdutoCreate.as_view(), name="cadastrar-produto"),


    path('atualizar/categoria/<int:pk>', CategoriaUpdate.as_view(), name="atualizar-categoria"),
    path('atualizar/produto/<int:pk>/', ProdutoUpdate.as_view(), name="atualizar-produto"),


    path('listar/categorias/', CategoriaList.as_view(), name="listar-categorias"),
    path('listar/usuarios/', PerfilList.as_view(), name="listar-usuarios"),
    path('listar/produtos/', ProdutoList.as_view(), name="listar-produtos"),
]