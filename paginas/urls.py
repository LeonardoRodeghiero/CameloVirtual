from django.urls import path
from .views import IndexView, AcessoNegadoView

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('sem-permissao/', AcessoNegadoView.as_view(), name="acesso-negado")
]
