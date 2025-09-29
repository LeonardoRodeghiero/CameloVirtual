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
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nome} - R${self.preco}'
    
class Carrinho(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='atualizado em')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Carrinho de {self.usuario}'

class Carrinho_Produto(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)

    def __str__(self):
        return f'Produto {self.produto.nome} no carrinho de {self.carrinho.usuario}'
    
    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['carrinho', 'produto'], name='unique_carrinho_produto')
            ]