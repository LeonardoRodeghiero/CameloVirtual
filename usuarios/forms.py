from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class UsuarioForm(UserCreationForm):
    email = forms.EmailField(max_length=100)
    nome_completo = forms.CharField(max_length=80)
    cpf = forms.CharField(max_length=14)
    telefone = forms.CharField(max_length=16)
    estado = forms.CharField(max_length=2)
    cidade = forms.CharField(max_length=70)

    class Meta():
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_email(self):
        e = self.cleaned_data['email']

        if User.objects.filter(email=e).exists():
            raise ValidationError(f'O email {e} já está em uso')
        
        return e


from .models import Perfil

class PerfilForm(forms.ModelForm):
    email = forms.EmailField(label='Email')

    class Meta:
        model = Perfil
        fields = [
            'nome_completo', 'tipo', 'cpf', 'telefone', 'cep', 'estado',
            'cidade', 'bairro', 'logradouro', 'numero', 'complemento'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Preenche o campo de e-mail com o valor atual do usuário
        if self.instance and self.instance.usuario:
            self.fields['email'].initial = self.instance.usuario.email
        
        ordem = [
            'nome_completo', 'tipo', 'cpf', 'email', 'telefone', 'cep', 'estado',
            'cidade', 'bairro', 'logradouro', 'numero', 'complemento'
        ]
        self.order_fields(ordem)

    def save(self, commit=True):
        perfil = super().save(commit=False)
        # Atualiza o e-mail do usuário vinculado
        perfil.usuario.email = self.cleaned_data['email']
        if commit:
            perfil.usuario.save()
            perfil.save()
        return perfil
