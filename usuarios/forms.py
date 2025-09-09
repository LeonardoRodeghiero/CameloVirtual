from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class UsuarioForm(UserCreationForm):
    ESTADO_CHOICES = [
        ('AC', 'ACRE'),
        ('AL', 'ALAGOAS'),
        ('AP', 'AMAPÁ'),
        ('AM', 'AMAZONAS'),
        ('BA', 'BAHIA'),
        ('CE', 'CEARÁ'),
        ('DF', 'DISTRITO FEDERAL'),
        ('ES', 'ESPÍRITO SANTO'),
        ('GO', 'GOIÁS'),
        ('MA', 'MARANHÃO'),
        ('MT', 'MATO GROSSO'),
        ('MS', 'MATO GROSSO DO SUL'),
        ('MG', 'MINAS GERAIS'),
        ('PA', 'PARÁ'),
        ('PB', 'PARAÍBA'),
        ('PR', 'PARANÁ'),
        ('PE', 'PERNAMBUCO'),
        ('PI', 'PIAUÍ'),
        ('RJ', 'RIO DE JANEIRO'),
        ('RN', 'RIO GRANDE DO NORTE'),
        ('RS', 'RIO GRANDE DO SUL'),
        ('RO', 'RONDÔNIA'),
        ('RR', 'RORAIMA'),
        ('SC', 'SANTA CATARINA'),
        ('SP', 'SÃO PAULO'),
        ('SE', 'SERGIPE'),
        ('TO', 'TOCANTINS'),
    ]

    email = forms.EmailField(max_length=100)
    nome_completo = forms.CharField(max_length=80)
    cpf = forms.CharField(max_length=14)
    telefone = forms.CharField(max_length=16)
    estado = forms.ChoiceField(choices=[('', '--- Selecione ---')] + ESTADO_CHOICES)
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

    TIPO_CHOICES = [
        ('cliente', 'Cliente'),
        ('administrador', 'Administrador'),
    ]


    ESTADO_CHOICES = [
        ('AC', 'ACRE'),
        ('AL', 'ALAGOAS'),
        ('AP', 'AMAPÁ'),
        ('AM', 'AMAZONAS'),
        ('BA', 'BAHIA'),
        ('CE', 'CEARÁ'),
        ('DF', 'DISTRITO FEDERAL'),
        ('ES', 'ESPÍRITO SANTO'),
        ('GO', 'GOIÁS'),
        ('MA', 'MARANHÃO'),
        ('MT', 'MATO GROSSO'),
        ('MS', 'MATO GROSSO DO SUL'),
        ('MG', 'MINAS GERAIS'),
        ('PA', 'PARÁ'),
        ('PB', 'PARAÍBA'),
        ('PR', 'PARANÁ'),
        ('PE', 'PERNAMBUCO'),
        ('PI', 'PIAUÍ'),
        ('RJ', 'RIO DE JANEIRO'),
        ('RN', 'RIO GRANDE DO NORTE'),
        ('RS', 'RIO GRANDE DO SUL'),
        ('RO', 'RONDÔNIA'),
        ('RR', 'RORAIMA'),
        ('SC', 'SANTA CATARINA'),
        ('SP', 'SÃO PAULO'),
        ('SE', 'SERGIPE'),
        ('TO', 'TOCANTINS'),
    ]


    tipo = forms.ChoiceField(choices=TIPO_CHOICES)
    estado = forms.ChoiceField(choices=ESTADO_CHOICES)
    class Meta:
        model = Perfil

        fields = [
            'nome_completo', 'tipo', 'cpf', 'telefone', 'cep', 'estado',
            'cidade', 'bairro', 'logradouro', 'numero', 'complemento'
        ]

    


    def __init__(self, *args, **kwargs):
        self.usuario_logado = kwargs.pop('usuario_logado', None)
        super().__init__(*args, **kwargs)
        # Preenche o campo de e-mail com o valor atual do usuário
        if self.instance and self.instance.usuario:
            self.fields['email'].initial = self.instance.usuario.email
        
        if self.usuario_logado.groups.filter(name='administrador').exists():    
            ordem = [
            'nome_completo', 'tipo', 'cpf', 'email', 'telefone', 'cep', 'estado',
            'cidade', 'bairro', 'logradouro', 'numero', 'complemento'
            ]
        else:
            self.fields.pop('tipo')

            ordem = [
                'nome_completo', 'cpf', 'email', 'telefone', 'cep', 'estado',
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
