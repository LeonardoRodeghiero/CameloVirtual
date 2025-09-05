from django.urls import path

from .views import CategoriaCreate
from .views import CategoriaList

urlpatterns = [
    
    path('cadastrar/categoria/', CategoriaCreate.as_view(), name="cadastrar-categoria"),
    path('listar/categorias/', CategoriaList.as_view(), name="listar-categorias"),
]