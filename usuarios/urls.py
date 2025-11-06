from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UsuarioCreate, PerfilUpdate, UsuarioDelete, login_email_view



urlpatterns = [
    path('login/', login_email_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),

    path('registrar/', UsuarioCreate.as_view(), name="registrar"),
    path('atualizar/perfil/<int:pk>/', PerfilUpdate.as_view(), name="atualizar-perfil"),
    path('excluir/perfil/<int:pk>/', UsuarioDelete.as_view(), name="excluir-perfil"),
]