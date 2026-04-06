from django.db import models

from django.contrib.auth.models import User

from django.core.validators import MinValueValidator, MaxValueValidator

import random
from django.utils import timezone 
from datetime import timedelta

from django.db.models import Avg, Count, F
# Create your models here.

class Camelo(models.Model):
    ESTADO_CHOICES = [
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    ]

    nome_fantasia = models.CharField(max_length=50)
    cnpj = models.CharField(max_length=18)
    email = models.EmailField(max_length=254, unique=True, blank=False, null=False,help_text="Insira E-mail para contato")    
    
    telefone = models.CharField(max_length=16)
    data_cadastro = models.DateTimeField(auto_now=True, verbose_name='cadastrado em')
    status = models.CharField(max_length=50, default="ativo")
    descricao_loja = models.CharField(max_length=100)
    imagem_logo = models.FileField(upload_to='pdf/')
    estado = models.CharField(max_length=2, choices=ESTADO_CHOICES, null=False)
    cidade = models.CharField(max_length=70, null=False)
    bairro = models.CharField(max_length=100, null=False)
    logradouro = models.CharField(max_length=100, null=False)
    numero = models.IntegerField(null=False)
    complemento = models.CharField(max_length=150, null=True, blank=True)
    cep = models.CharField(max_length=9, null=False, verbose_name="CEP")


    usuarios = models.ManyToManyField( 
        User,
        through="Camelo_Usuario", 
        related_name="camelos" 
        )

    def __str__(self): 
        return f"{self.nome_fantasia} ({self.cnpj})"


# class CameloPendente(models.Model):
#     nome_fantasia = models.CharField(max_length=50)
#     cnpj = models.CharField(max_length=18)
#     email = models.EmailField(max_length=254, unique=True, blank=False, null=False,help_text="Insira E-mail para contato")    
    
#     telefone = models.CharField(max_length=16)
#     data_cadastro = models.DateTimeField(auto_now=True, verbose_name='cadastrado em')
#     status = models.CharField(max_length=50, default="ativo")
#     descricao_loja = models.CharField(max_length=100)
#     imagem_logo = models.FileField(upload_to='pdf/')
#     endereco = models.CharField(max_length=150)


#     usuarios = models.ManyToManyField( 
#         User,
#         through="Camelo_Usuario_Pendente", 
#         related_name="camelos_pendente" 
#         )

#     def gerar_codigo(self):
#         self.codigo = str(random.randint(100000, 999999))
#         self.save()
    
#     def gerar_codigo_sms(self):
#         self.codigo_sms = str(random.randint(100000, 999999))
#         self.save()

#     def expirado(self): 
#         return timezone.now() > self.criado_em + timedelta(seconds=600)




class Camelo_Usuario(models.Model):
    camelo = models.ForeignKey(Camelo, related_name="relacoes_usuarios", on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Usuário {self.usuario.nome_completo} no camelô {self.camelo.nome_fantasia}'
    
    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['camelo', 'usuario'], name='unique_camelo_usuario')
            ]



class Categoria(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.CharField(max_length=80, null=True, blank=True, verbose_name="Descrição")
    camelo = models.ForeignKey(Camelo, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome}"


class ProdutoManager(models.Manager):
    def melhores_avaliados(self, limite=10):
        """
        Retorna os produtos com maior nota média, 
        usando a quantidade de vendas como critério de desempate.
        """
        return self.annotate(
            # Calculamos a média real baseada nas instâncias de Avaliacao
            media_calculada=Avg('avaliacoes__nota'),
            total_votos=Count('avaliacoes')
        ).filter(
            total_votos__gt=0 # Opcional: apenas produtos que já foram avaliados
        ).order_by('-media_calculada', '-quantidade_vendido')[:limite]



class Produto(models.Model):
    nome = models.CharField(max_length=100)
    marca = models.CharField(max_length=50)
    descricao = models.CharField(max_length=150, verbose_name='Descrição')
    preco = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Preço')
    quantidade = models.IntegerField()
    quantidade_vendido = models.IntegerField(default=0, verbose_name="Quantidade Vendido")
    imagem = models.FileField(upload_to='pdf/')
    avaliacao_geral = models.DecimalField(max_digits=2, decimal_places=1, default=0, verbose_name="Avaliação Geral")
    fornecedor = models.CharField(max_length=50)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    camelo = models.ForeignKey(Camelo, on_delete=models.CASCADE)


    objects = ProdutoManager()

    def __str__(self):
        return f'{self.nome} - R${self.preco} ({self.camelo.nome_fantasia})'
    


class Carrinho(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='atualizado em')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Carrinho de {self.usuario}'
    
    def total_valor(self):
        return sum(item.quantidade * item.produto.preco for item in self.produtos.all())


class Pedido(models.Model):
    valor_total = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Valor Total')
    data_pedido = models.DateTimeField(auto_now=True, verbose_name='data do pedido')
    opcao_pedido = models.CharField(max_length=30, choices=[("casa", "Receber em casa"), ("loja", "Buscar na loja")], null=False, default="Receber em casa")
    endereco = models.CharField(max_length=150, null=True, verbose_name="endereço")

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return f'Pedido de {self.usuario.username}'


class Avaliacao(models.Model):
    nota = models.IntegerField(verbose_name='Nota', validators=[MinValueValidator(1), MaxValueValidator(5)])
    data_hora_mensagem = models.DateTimeField(auto_now=True, verbose_name='data e hora da avaliação')
    mensagem = models.CharField(max_length=255, null=False, verbose_name="mensagem da avalição")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=True, related_name="avaliacoes")
    camelo = models.ForeignKey(Camelo, on_delete=models.CASCADE, null=True)


    def __str__(self):
        if self.camelo is None:
            txt = f'Avaliação de {self.usuario.username} no produto {self.produto.nome}'
        if self.produto is None:
            txt = f'Avaliação de {self.usuario.username} no camelô {self.camelo.nome_fantasia}'


        return txt


class Pedido_Produto(models.Model):
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço Unitário')
    quantidade = models.IntegerField()
    status = models.CharField(max_length=30, null=False, default="em andamento")

    pedido = models.ForeignKey(Pedido, related_name="produtos", on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)

    def __str__(self):
        return f'Produto {self.produto.nome} no pedido de {self.pedido.usuario.nome_completo} com id {self.pedido.pk}'

    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['pedido', 'produto'], name='unique_pedido_produto')
            ]


class Carrinho_Produto(models.Model):
    carrinho = models.ForeignKey(Carrinho, related_name="produtos", on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.DO_NOTHING)
    quantidade = models.IntegerField(default=1)

    def __str__(self):
        return f'Produto {self.produto.nome} no carrinho de {self.carrinho.usuario}'
    
    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['carrinho', 'produto'], name='unique_carrinho_produto')
            ]