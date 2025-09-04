from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class UsuarioForm(UserCreationForm):
    email = forms.EmailField(max_length=100)
    nome_completo = forms.CharField(max_length=80)
    cpf = forms.CharField(max_length=14)
    telefone = forms.CharField(max_length=16)
    cidade = forms.CharField(max_length=70)

    class Meta():
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_email(self):
        e = self.cleaned_data['email']

        if User.objects.filter(email=e).exists():
            raise ValidationError(f'O email {e} já está em uso')
        
        return e
