from django.urls import path

from .views import CategoriaCreate

urlpatterns = [
    
    path('categoria/', CategoriaCreate.as_view(), name="cadastrar-categoria"),
]