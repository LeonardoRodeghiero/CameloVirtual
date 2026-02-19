from django.db import models

from django.contrib.auth.models import User
# Create your models here.

class Camelo(models.Model):
    nome_fantasia = models.CharField(max_length=50)
    cnpj = models.CharField(max_length=18)
    email = models.EmailField(max_length=254, unique=True, blank=False, null=False,help_text="Insira E-mail para contato")    
    
    telefone = models.CharField(max_length=16)
    data_cadastro = models.DateTimeField(auto_now=True, verbose_name='cadastrado em')
    status = models.CharField(max_length=50, default="ativo")
    descricao_loja = models.CharField(max_length=100)
    imagem_logo = models.FileField(upload_to='pdf/')
    endereco = models.CharField(max_length=150)


    usuarios = models.ManyToManyField( 
        User,
        through="Camelo_Usuario", 
        related_name="camelos" 
        )

    def __str__(self): 
        return f"{self.nome_fantasia} ({self.cnpj})"

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


    def __str__(self):
        return f'{self.nome} - R${self.preco}'
    
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
    status = models.CharField(max_length=30, null=False, default="em andamento")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return f'Pedido de {self.usuario.nome_completo} no camelô {self.camelo.nome_fantasia}'


class Avaliacao(models.Model):
    nota = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Valor Total')
    data_hora_mensagem = models.DateTimeField(auto_now=True, verbose_name='data do pedido')
    mensagem = models.CharField(max_length=30, null=False, default="em andamento")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=True)
    camelo = models.ForeignKey(Camelo, on_delete=models.CASCADE, null=True)


    def __str__(self):
        if self.camelo == null:
            txt = f'Avaliação de {self.usuario.nome_completo} no produto {self.produto.nome}'
        if self.produto == null:
            txt = f'Avaliação de {self.usuario.nome_completo} no camelô {self.camelo.nome_fantasia}'


        return txt


class Pedido_Produto(models.Model):
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço Unitário')
    quantidade = models.IntegerField()
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