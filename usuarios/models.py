from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Perfil(models.Model):
    nome_completo = models.CharField(max_length=80, null=False)
    cpf = models.CharField(max_length=14, null=False, verbose_name="CPF", unique=True)
    telefone = models.CharField(max_length=16, null=False, unique=True)
    tipo = models.CharField(max_length=30, null=False, default="cliente")
    estado = models.CharField(max_length=2, null=False)
    cidade = models.CharField(max_length=70, null=False)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    logradouro = models.CharField(max_length=100, null=True, blank=True)
    numero = models.IntegerField(null=True, blank=True)
    complemento = models.CharField(max_length=150, null=True, blank=True)
    cep = models.CharField(max_length=9, null=True, blank=True, verbose_name="CEP")


    usuario = models.OneToOneField(User, on_delete=models.CASCADE)


    def __str__(self):
        return f'{self.nome_completo}'

