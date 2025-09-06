from django.db import models

from django.contrib.auth.models import User
# Create your models here.

class Categoria(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.CharField(max_length=80, null=True, blank=True)

    def __str__(self):
        return f"{self.nome}"

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    marca = models.CharField(max_length=50)
    descricao = models.CharField(max_length=150, verbose_name='descrição')
    preco = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='preço')
    quantidade = models.IntegerField()
    quantidade_vendido = models.IntegerField(default=0)
    imagem = models.FileField(upload_to='pdf/')
    avaliacao_geral = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.nome} - R${self.preco}'

