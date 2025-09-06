from django.urls import path

from .views import CategoriaCreate

from .views import CategoriaUpdate

from .views import CategoriaList, PerfilList

urlpatterns = [
    
    path('cadastrar/categoria/', CategoriaCreate.as_view(), name="cadastrar-categoria"),

    path('atualizar/categoria/<int:pk>', CategoriaUpdate.as_view(), name="atualizar-categoria"),



    path('listar/categorias/', CategoriaList.as_view(), name="listar-categorias"),
    path('listar/usuarios/', PerfilList.as_view(), name="listar-usuarios"),
]