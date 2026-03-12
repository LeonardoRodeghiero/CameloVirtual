# forms.py
from django import forms
# from usuarios.models import Perfil

class BuscarUsuarioForm(forms.Form):
    cpf = forms.CharField(max_length=14, label="CPF do usuário")

    # def clean_cpf(self):
    #     cpf = self.cleaned_data["cpf"]
    #     try:
    #         perfil = Perfil.objects.get(cpf=cpf)
    #     except Perfil.DoesNotExist:
    #         raise forms.ValidationError("Nenhum usuário encontrado com esse CPF.")
    #     return cpf

    # def get_usuario(self):
    #     cpf = self.cleaned_data["cpf"]
    #     perfil = Perfil.objects.get(cpf=cpf)
    #     return perfil.usuario