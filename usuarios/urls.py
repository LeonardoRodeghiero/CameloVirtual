from django.urls import path
from django.contrib.auth import views as auth_views
from .views import UsuarioCreate, PerfilUpdate, UsuarioDelete, login_email_view, confirmar_codigo



urlpatterns = [
    path('login/', login_email_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),

    path('registrar/', UsuarioCreate.as_view(), name="registrar"),
    path("confirmar/<str:email>/", confirmar_codigo, name="confirmar-codigo"),

    path('atualizar/perfil/<int:pk>/', PerfilUpdate.as_view(), name="atualizar-perfil"),
    path('excluir/perfil/<int:pk>/', UsuarioDelete.as_view(), name="excluir-perfil"),



    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="usuarios/registration/password_reset.html"), name="reset_password"), 
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="usuarios/registration/password_reset_sent.html"), name="password_reset_done"), 
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="usuarios/registration/password_reset_confirm.html"), name="password_reset_confirm"), 
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="usuarios/registration/password_reset_complete.html"), name="password_reset_complete"),
]