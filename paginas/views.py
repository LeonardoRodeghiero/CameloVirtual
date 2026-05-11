from django.views.generic import TemplateView



from cadastros.views import Produto, Carrinho_Produto, Carrinho, Camelo, Pedido_Produto

from cadastros.models import Produto, Avaliacao, Camelo, Camelo_Usuario, Pedido, Pedido_Produto, Categoria
from cadastros.forms import AvaliacaoForm

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View

from django.shortcuts import get_object_or_404, redirect, render, reverse

from django.http import JsonResponse

from django.utils import timezone

from django.contrib.auth.models import User

from .forms import BuscarUsuarioForm

from django.views.generic import FormView

from usuarios.models import Perfil

from django.db.models import Count

from django.utils import timezone

from datetime import datetime

from django.db import transaction

from django.contrib.auth.mixins import LoginRequiredMixin

import resend


# Create your views here.


class IndexView(TemplateView):
    template_name = "paginas/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        usuario = self.request.user


        # 1. Buscamos os produtos usando o Manager que criamos
        melhores_produtos_qs = Produto.objects.melhores_avaliados().annotate(
            qtd_total_avaliacoes=Count('avaliacoes_produto')
        )
        # 2. Criamos a lista customizada com a lógica das estrelas
        lista_customizada = []
        for produto in melhores_produtos_qs:
            # Lógica para estrelas (usando o campo avaliacao_geral do seu Model)
            inteira = int(produto.avaliacao_geral)
            tem_meia = (produto.avaliacao_geral - inteira) >= 0.5
            
            lista_customizada.append({
                'produto': produto,
                'media_avaliacoes': round(produto.avaliacao_geral, 1),
                'media_inteira': range(inteira),
                'tem_meia': tem_meia,
                'qtd_avaliacoes': produto.qtd_total_avaliacoes, 
            })

        lista_customizada_camelos = []

        if self.request.user.is_authenticated:
            camelos = Camelo_Usuario.objects.filter(usuario=usuario).annotate(
                qtd_total_avaliacoes_camelo=Count('camelo__avaliacoes_camelo')
            )

            for item in camelos:
            # Lógica para estrelas (usando o campo avaliacao_geral do seu Model)
                inteira = int(item.camelo.avaliacao_geral)
                tem_meia = (item.camelo.avaliacao_geral - inteira) >= 0.5
                
                lista_customizada_camelos.append({
                    'camelo': item.camelo,
                    'media_avaliacoes': round(item.camelo.avaliacao_geral, 1),
                    'media_inteira': range(inteira),
                    'tem_meia': tem_meia,
                    'qtd_avaliacoes': item.qtd_total_avaliacoes_camelo, 
                })

        else:
            camelos = None

        

        

        # 3. Enviamos para o contexto
        context['melhores_produtos'] = lista_customizada
        context['camelos'] = Camelo.objects.all()
        context['camelos_que_faz_parte'] = lista_customizada_camelos

        
        return context

class EmailConfirmacaoView(TemplateView):
    template_name = "paginas/confirmar.html"


class CameloView(TemplateView):
    template_name = "paginas/camelo_padrao.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        camelo_id = self.kwargs.get("pk")
        camelo = get_object_or_404(Camelo, id=camelo_id)
        usuario = self.request.user

        lista_customizada_camelo = []

        melhores_produtos_qs_camelo = (
            Produto.objects.filter(camelo=camelo)
            .melhores_avaliados_camelo()
            .annotate(qtd_total_avaliacoes=Count('avaliacoes_produto'))
        )

        for produto in melhores_produtos_qs_camelo:
            # Lógica para estrelas (usando o campo avaliacao_geral do seu Model)
            inteira = int(produto.avaliacao_geral)
            tem_meia = (produto.avaliacao_geral - inteira) >= 0.5
            
            lista_customizada_camelo.append({
                'produto': produto,
                'media_avaliacoes': round(produto.avaliacao_geral, 1),
                'media_inteira': range(inteira),
                'tem_meia': tem_meia,
                'qtd_avaliacoes': produto.qtd_total_avaliacoes, 
            })

        context['melhores_produtos_camelo'] = lista_customizada_camelo





        pode_avaliar =  Camelo_Usuario.objects.filter(camelo=camelo).exists()

        avaliacoes = Avaliacao.objects.filter(camelo=camelo)

        # Forma para meia estrela
        inteira = int(camelo.avaliacao_geral)
        tem_meia = (camelo.avaliacao_geral - inteira) >= 0.5
        context["media_avaliacoes"] = round(camelo.avaliacao_geral, 1)
        context["media_inteira"] = inteira
        context["media_meia"] = tem_meia



        context['form'] = AvaliacaoForm()
        context['avaliacoes'] = avaliacoes
        context['qtd_avaliacoes'] = avaliacoes.count()

        if usuario.is_authenticated:
            ja_avaliou = Avaliacao.objects.filter(camelo=camelo, usuario=usuario).exists()


            context['ja_avaliou'] = ja_avaliou  
            context['pode_avaliar'] = pode_avaliar    
        





        camelo_id = self.kwargs.get("pk")
        camelo = get_object_or_404(Camelo, pk=camelo_id)
        context["camelo"] = camelo
        return context

    def post(self, request, *args, **kwargs):
        camelo_id = self.kwargs.get("pk")
        camelo = get_object_or_404(Camelo, id=camelo_id)

        form = AvaliacaoForm(request.POST)

        
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.usuario = request.user
            avaliacao.camelo = camelo
            avaliacao.save()
            return redirect('camelo', pk=camelo.pk)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class AcessoNegadoView(TemplateView):
    template_name = 'paginas/acesso_negado.html'

class AcessoNegadoCameloView(TemplateView):
    template_name = 'paginas/camelo/acesso_negado_camelo.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        
        camelo_id = self.kwargs.get("pk") 
        camelo = get_object_or_404(Camelo, pk=camelo_id) 
        context["camelo"] = camelo

        return context

class ClienteProdutoList(ListView):


    model = Produto
    template_name = 'paginas/produtos.html'
    context_object_name = 'produtos'

    
    def get_queryset(self):
        queryset = Produto.objects.annotate(qtd_total_avaliacoes=Count('avaliacoes_produto'))

        txt_nome = self.request.GET.get('nome')

        if txt_nome:
            queryset = queryset.filter(nome__icontains=txt_nome)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        produtos_originais = context['produtos']

        lista_customizada = []

        for produto in produtos_originais:
            # Forma para meia estrela
            inteira = int(produto.avaliacao_geral)
            tem_meia = (produto.avaliacao_geral - inteira) >= 0.5
            

            item = {
                'produto': produto,
                'media_avaliacoes': round(produto.avaliacao_geral, 1),
                'media_inteira': range(inteira),
                'tem_meia': tem_meia,
                'qtd_avaliacoes': produto.qtd_total_avaliacoes,
            }
            lista_customizada.append(item)


         
        context['lista_com_dados'] = lista_customizada
        return context


class ClienteCameloList(ListView):


    model = Camelo
    template_name = 'paginas/camelo/camelos.html'
    context_object_name = 'camelos'

    
    def get_queryset(self):
        txt_nome = self.request.GET.get('nome_fantasia')
        queryset = Camelo.objects.annotate(qtd_total_avaliacoes=Count('avaliacoes_camelo')).distinct()

        if txt_nome:
            queryset = queryset.filter(nome_fantasia__icontains=txt_nome)
        

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        camelos_originais = context['camelos']

        lista_customizada = []

        for camelo in camelos_originais:
            # Forma para meia estrela
            inteira = int(camelo.avaliacao_geral)
            tem_meia = (camelo.avaliacao_geral - inteira) >= 0.5
            

            item = {
                'camelo': camelo,
                'media_avaliacoes': round(camelo.avaliacao_geral, 1),
                'media_inteira': range(inteira),
                'tem_meia': tem_meia,
                'qtd_avaliacoes': camelo.qtd_total_avaliacoes,
            }
            lista_customizada.append(item)


         
        context['lista_com_dados'] = lista_customizada
        return context

class ClienteProdutoCameloList(ListView):


    model = Produto
    template_name = 'paginas/camelo/produtos-camelo.html'
    context_object_name = 'produtos'

    
    def get_queryset(self):

        camelo_id = self.kwargs.get("pk")
        queryset = Produto.objects.annotate(qtd_total_avaliacoes=Count('avaliacoes_produto'))

        txt_nome = self.request.GET.get('nome')

        if txt_nome:
            queryset = queryset.filter(nome__icontains=txt_nome, camelo_id=camelo_id)
        else:
            queryset = queryset.filter(camelo_id=camelo_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        produtos_originais = context['produtos']

        lista_customizada = []

        for produto in produtos_originais:
            # Forma para meia estrela
            inteira = int(produto.avaliacao_geral)
            tem_meia = (produto.avaliacao_geral - inteira) >= 0.5
            

            item = {
                'produto': produto,
                'media_avaliacoes': round(produto.avaliacao_geral, 1),
                'media_inteira': range(inteira),
                'tem_meia': tem_meia,
                'qtd_avaliacoes': produto.qtd_total_avaliacoes,
            }
            lista_customizada.append(item)

        camelo_id = self.kwargs.get("pk") 
        
        camelo = get_object_or_404(Camelo, pk=camelo_id) 
        context["camelo"] = camelo
         
        context['lista_com_dados'] = lista_customizada
        return context


class ProdutoEspecifico(DetailView):
    model = Produto
    template_name = 'paginas/produto.html'
    context_object_name = 'produto'

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        produto = self.object
        usuario = self.request.user

        ja_avaliou = Avaliacao.objects.filter(produto=produto, usuario=usuario).exists()

        pode_avaliar = Pedido_Produto.objects.filter(produto=produto, pedido__usuario=usuario, status="finalizado").exists()  #AQUI VAI TER QUE MUDAR O STATUS PAA APONTAR PARA PEDIDO_PRODUTO

        avaliacoes = Avaliacao.objects.filter(produto=produto)

        # Forma para meia estrela
        inteira = int(produto.avaliacao_geral)
        tem_meia = (produto.avaliacao_geral - inteira) >= 0.5
        context["media_avaliacoes"] = round(produto.avaliacao_geral, 1)
        context["media_inteira"] = inteira
        context["media_meia"] = tem_meia



        context['form'] = AvaliacaoForm()
        context['avaliacoes'] = avaliacoes
        context['qtd_avaliacoes'] = avaliacoes.count()

        if usuario.is_authenticated:
            context['ja_avaliou'] = ja_avaliou  
            context['pode_avaliar'] = pode_avaliar    
        
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.usuario = request.user
            avaliacao.produto = self.object
            avaliacao.save()
            return redirect('produto', pk=self.object.pk)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class ProdutoCameloEspecifico(DetailView):
    # model = Produto
    # template_name = 'paginas/camelo/produto-camelo.html'

    # def get_object(self, queryset=None): 
    #     produto_id = self.kwargs.get("produto_id") 
    #     camelo_id = self.kwargs.get("camelo_id") # garante que só pega produto do camelô atual 
    #     return get_object_or_404(Produto, pk=produto_id, camelo_id=camelo_id)

    # def get_context_data(self, **kwargs): 
    #     context = super().get_context_data(**kwargs) 
    #     camelo_id = self.kwargs.get("camelo_id") 
    #     camelo = get_object_or_404(Camelo, pk=camelo_id) 
    #     context["camelo"] = camelo 
    #     return context


    model = Produto
    template_name = 'paginas/camelo/produto-camelo.html'
    context_object_name = 'produto'

    def get_object(self, queryset=None):
        # Captura os IDs da URL
        camelo_id = self.kwargs.get("camelo_id")
        produto_id = self.kwargs.get("produto_id")
        
        # Busca o produto garantindo que ele pertence ao camelô da URL
        return get_object_or_404(Produto, pk=produto_id, camelo_id=camelo_id)



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        produto = self.object
        usuario = self.request.user

        ja_avaliou = Avaliacao.objects.filter(produto=produto, usuario=usuario)
        pode_avaliar = Pedido_Produto.objects.filter(produto=produto, pedido__usuario=usuario, status="finalizado").exists()  #AQUI VAI TER QUE MUDAR O STATUS PAA APONTAR PARA PEDIDO_PRODUTO


        avaliacoes = Avaliacao.objects.filter(produto=produto)

        context["camelo"] = get_object_or_404(Camelo, pk=self.kwargs.get("camelo_id"))



        # Forma para meia estrela
        inteira = int(produto.avaliacao_geral)
        tem_meia = (produto.avaliacao_geral - inteira) >= 0.5
        context["media_avaliacoes"] = round(produto.avaliacao_geral, 1)
        context["media_inteira"] = inteira
        context["media_meia"] = tem_meia



        context['form'] = AvaliacaoForm()
        context['avaliacoes'] = avaliacoes
        context['qtd_avaliacoes'] = avaliacoes.count()

        if usuario.is_authenticated:
            context['ja_avaliou'] = ja_avaliou
            context['pode_avaliar'] = pode_avaliar    

        return context

    # def post(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     form = AvaliacaoForm(request.POST)
    #     if form.is_valid():
    #         avaliacao = form.save(commit=False)
    #         avaliacao.usuario = request.user
    #         avaliacao.produto = self.object
    #         avaliacao.save()
    #         return redirect('produto', pk=self.object.pk)
    #     context = self.get_context_data(form=form)
    #     return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.usuario = request.user
            avaliacao.produto = self.object
            avaliacao.save()
            # Redireciona para a mesma página (mantendo os IDs da URL)
            return redirect('produto-camelo', 
                            camelo_id=self.kwargs.get("camelo_id"), 
                            produto_id=self.object.pk)
        
        return self.render_to_response(self.get_context_data(form=form))
class VerCarrinho(ListView):
    model = Carrinho_Produto
    template_name = 'paginas/ver_carrinho.html'
    context_object_name = 'itens'

    def get_queryset(self):
        carrinho = Carrinho.objects.filter(usuario=self.request.user)

        if carrinho.exists():
            carrinho = Carrinho.objects.get(usuario=self.request.user)
            return Carrinho_Produto.objects.filter(carrinho=carrinho)
        else:
            return Carrinho_Produto.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        carrinho = Carrinho.objects.filter(usuario=self.request.user).first()
        context['carrinho'] = carrinho
        total = sum(item.produto.preco * item.quantidade for item in context['itens'])
        context['total'] = total
        return context
    


class VerHistoricoPedidos(ListView):
    model = Pedido_Produto
    template_name = 'paginas/historico_pedidos.html'
    context_object_name = 'itens'

    def get_queryset(self):
        pedidos = Pedido.objects.filter(usuario=self.request.user)

        if pedidos.exists():
            return Pedido_Produto.objects.filter(pedido__in=pedidos)
        else:
            return Pedido_Produto.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        pedidos = Pedido.objects.filter(usuario=self.request.user)

        context['tem_pedido'] = pedidos.exists()

        base_query = Pedido_Produto.objects.select_related('pedido', 'produto').filter(
            pedido__usuario=self.request.user
        ).order_by('-pedido__data_pedido')



        pedidos_andamento = base_query.filter(status='em andamento')
        pedidos_finalizado = base_query.filter(status='finalizado')
        pedidos_cancelado = base_query.filter(status='cancelado')

        context['pedidos_andamento'] = pedidos_andamento
        context['pedidos_finalizado'] = pedidos_finalizado
        context['pedidos_cancelado'] = pedidos_cancelado


        
        return context
# class AlterarQuantidadeView(View):
#     def post(self, request, item_id, acao):
#         item = get_object_or_404(Carrinho_Produto, id=item_id, carrinho__usuario=request.user)

#         if acao == 'incrementar':
#             item.quantidade += 1
#         elif acao == 'diminuir':
#             item.quantidade = max(1, item.quantidade - 1)  # evita quantidade zero
#         item.save()

#         return JsonResponse({'quantidade': item.quantidade})   
     
def alterar_quantidade(request, item_id, acao):
    item = get_object_or_404(Carrinho_Produto, id=item_id)

    if acao == 'incrementar':
        item.quantidade += 1
    elif acao == 'diminuir' and item.quantidade > 1:
        item.quantidade -= 1

    item.save()

    Carrinho.objects.filter(pk=item.carrinho.pk).update(atualizado_em=timezone.now())

    carrinho = item.carrinho
    total = sum(prod.produto.preco * prod.quantidade for prod in Carrinho_Produto.objects.filter(carrinho=item.carrinho))


    return JsonResponse({'quantidade': item.quantidade,
                        'total': f'{total:.2f}'.replace('.', ',')
                    })


class InserirFuncionarioView(FormView):
    template_name = "paginas/camelo/inserir_funcionario.html"
    form_class = BuscarUsuarioForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        camelo_id = self.kwargs.get("pk")
        camelo = get_object_or_404(Camelo, pk=camelo_id)
        context["camelo"] = camelo
        return context

    def form_valid(self, form):
        camelo = get_object_or_404(Camelo, pk=self.kwargs.get("pk"))
        cpf = form.cleaned_data["cpf"]

        try:
            perfil = Perfil.objects.get(cpf=cpf)
        except Perfil.DoesNotExist:
            form.add_error("cpf", "Nenhum usuário encontrado com esse CPF.")
            return self.form_invalid(form)


        return render(self.request, "paginas/camelo/confirmar_funcionario.html", {
            "camelo": camelo,
            "perfil": perfil
        })





        # perfil = get_object_or_404(Perfil, cpf=cpf)
        # usuario = perfil.usuario

        # Camelo_Usuario.objects.get_or_create(camelo=camelo, usuario=usuario)

        # return redirect("camelo", pk=camelo.pk)



class ConfirmarFuncionarioView(View):
    def post(self, request, pk, perfil_pk):
        camelo = get_object_or_404(Camelo, pk=pk)
        perfil = get_object_or_404(Perfil, pk=perfil_pk)
        usuario = perfil.usuario

        Camelo_Usuario.objects.get_or_create(camelo=camelo, usuario=usuario)
        return redirect("camelo", pk=camelo.pk)

        
class ConfirmarEndereco(View):
    def get(self, request):
        dados = request.session.get('pedido_temp')
        if not dados:
            return redirect("index")

        perfil = getattr(request.user, "perfil", None)
        endereco_padrao = ""
        if perfil:
            endereco_padrao = f"{perfil.logradouro or ''}, {perfil.numero or ''}, {perfil.complemento or ''} - {perfil.bairro or ''}, {perfil.cidade or ''}/{perfil.estado or ''}, CEP {perfil.cep or ''}"

        return render(request, "paginas/confirmar_endereco.html", {
            "endereco_padrao": endereco_padrao.strip(", -")
        })

    def post(self, request):
        dados = request.session.get('pedido_temp')
        if not dados:
            return redirect("index")

        endereco = request.POST.get("endereco")
        if not endereco:
            return render(request, "paginas/confirmar_endereco.html", {"erro": "Informe um endereço válido"})

        try:
            with transaction.atomic():
                if dados.get('origem') == 'carrinho':
                    # --- LÓGICA PARA CARRINHO ---
                    carrinho = get_object_or_404(Carrinho, usuario=request.user)
                    
                    # 1. Calcula o valor total do carrinho
                    total = sum(item.produto.preco * item.quantidade for item in carrinho.produtos.all())

                    # 2. Cria o Pedido principal (Pedido Model)
                    pedido = Pedido.objects.create(
                        usuario=request.user,
                        valor_total=total,
                        data_pedido=timezone.now(),
                        opcao_pedido=dados.get('opcao_pedido', 'casa'),
                        endereco=endereco
                    )

                    # 3. Loop nos itens do carrinho criando Pedido_Produto para cada um
                    for item in carrinho.produtos.all():
                        Pedido_Produto.objects.create(
                            pedido=pedido,
                            produto=item.produto,
                            quantidade=item.quantidade,
                            status="em andamento",
                            preco_unitario=item.produto.preco
                        )

                    # 4. Deleta o carrinho do banco
                    carrinho.produtos.all().delete()

                else:
                    # --- LÓGICA PARA PRODUTO DIRETO ---
                    produto = get_object_or_404(Produto, id=dados['produto_id'])
                    quantidade = dados['quantidade']

                    pedido = Pedido.objects.create(
                        usuario=request.user,
                        valor_total=produto.preco * quantidade,
                        data_pedido=timezone.now(),
                        opcao_pedido=dados['opcao_pedido'],
                        endereco=endereco
                    )

                    Pedido_Produto.objects.create(
                        pedido=pedido,
                        produto=produto,
                        quantidade=quantidade,
                        status="em andamento",

                        preco_unitario=produto.preco
                    )

        # Se chegou aqui, a transação foi um sucesso. Limpa a sessão.
            del request.session['pedido_temp']
            return redirect("index")

        except Exception as e:
        # Caso dê algum erro inesperado no banco de dados, aponta o erro no template
            return render(request, "paginas/confirmar_endereco.html", {"erro": f"Erro ao processar pedido: {e}"})


        # produto = get_object_or_404(Produto, id=dados['produto_id'])
        # quantidade = dados['quantidade']

        # pedido = Pedido.objects.create(
        #     usuario=request.user,
        #     valor_total=produto.preco * quantidade,
        #     data_pedido=timezone.now(),
        #     status="em andamento",
        #     opcao_pedido=dados['opcao_pedido'],
        #     endereco=endereco
        # )

        # Pedido_Produto.objects.create(
        #     pedido=pedido,
        #     produto=produto,
        #     quantidade=quantidade,
        #     preco_unitario=produto.preco
        # )

        # # limpa sessão
        # del request.session['pedido_temp']

        # return redirect("index")
  

class ProdutoCameloCategoriaList(ListView):
    model = Produto
    template_name = 'paginas/camelo/produtos-camelo.html'
    context_object_name = 'produtos'

    def get_queryset(self):
        # 1. Pegamos os IDs necessários
        camelo_id = self.kwargs.get("camelo_id")
        categoria_id = self.request.GET.get('categoria') # Vem do ?categoria=ID

        # 2. Começamos o queryset com o annotate que você já usa
        queryset = Produto.objects.filter(camelo_id=camelo_id).annotate(
            qtd_total_avaliacoes=Count('avaliacoes_produto')
        )

        # 3. Filtramos pela categoria se ela foi passada
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Reaproveitando sua lógica exata de processamento de estrelas
        produtos_filtrados = context['produtos']
        lista_customizada = []

        for produto in produtos_filtrados:
            inteira = int(produto.avaliacao_geral)
            tem_meia = (produto.avaliacao_geral - inteira) >= 0.5

            item = {
                'produto': produto,
                'media_avaliacoes': round(produto.avaliacao_geral, 1),
                'media_inteira': range(inteira),
                'tem_meia': tem_meia,
                'qtd_avaliacoes': produto.qtd_total_avaliacoes,
            }
            lista_customizada.append(item)

        # Adicionando o objeto Camelo ao contexto
        camelo_id = self.kwargs.get("camelo_id")
        context["camelo"] = get_object_or_404(Camelo, pk=camelo_id)
        context['lista_com_dados'] = lista_customizada
        
        return context


class FinalizarPedidoView(View):
    def get(self, request, pk):
        # Busca o objeto ou retorna 404 se não existir


        objeto = get_object_or_404(Pedido_Produto, pk=pk)

        produto = objeto.produto
        
        camelo_id = objeto.produto.camelo.id

        produto.quantidade_vendido += objeto.quantidade

        produto.save()

        # Alterando o status
        objeto.status = 'finalizado' 

        objeto.save()
        
        # Redireciona de volta
        return redirect(reverse('listar-pedidos-camelo', kwargs={'camelo_id': camelo_id}))


class CancelarPedidoView(View):
    def get(self, request, pk):
        objeto = get_object_or_404(Pedido_Produto, pk=pk)
        
        camelo_id = objeto.produto.camelo.id

        objeto.produto.quantidade += objeto.quantidade
        objeto.produto.save()


        # Alterando o status
        objeto.status = 'cancelado'
        objeto.save()
        
        return redirect(reverse('listar-pedidos-camelo', kwargs={'camelo_id': camelo_id}))


class AvaliacoesCamelo(TemplateView):
    template_name = 'paginas/camelo/avaliacoes_camelo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        camelo_id = self.kwargs.get("pk")
        camelo = get_object_or_404(Camelo, id=camelo_id)
        usuario = self.request.user

        

        pode_avaliar = Pedido_Produto.objects.filter(produto__camelo=camelo, pedido__usuario=usuario, status="finalizado").exists()

        avaliacoes = Avaliacao.objects.filter(camelo=camelo)

        # Forma para meia estrela
        inteira = int(camelo.avaliacao_geral)
        tem_meia = (camelo.avaliacao_geral - inteira) >= 0.5
        context["media_avaliacoes"] = round(camelo.avaliacao_geral, 1)
        context["media_inteira"] = inteira
        context["media_meia"] = tem_meia



        context['form'] = AvaliacaoForm()
        context['avaliacoes'] = avaliacoes
        context['qtd_avaliacoes'] = avaliacoes.count()

        if usuario.is_authenticated:
            ja_avaliou = Avaliacao.objects.filter(camelo=camelo, usuario=usuario).exists()


            context['ja_avaliou'] = ja_avaliou  
            context['pode_avaliar'] = pode_avaliar    
        





        camelo_id = self.kwargs.get("pk")
        camelo = get_object_or_404(Camelo, pk=camelo_id)
        context["camelo"] = camelo
        return context
    
    def post(self, request, *args, **kwargs):
        camelo_id = self.kwargs.get("pk")
        camelo = get_object_or_404(Camelo, id=camelo_id)

        form = AvaliacaoForm(request.POST)

        
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.usuario = request.user
            avaliacao.camelo = camelo
            avaliacao.save()
            return redirect('todas-avaliacoes-camelo', pk=camelo.pk)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)



class CameloPerfilList(LoginRequiredMixin, ListView):


    model = Camelo_Usuario
    template_name = 'paginas/camelo/camelo_usuarios_lista.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou a URL personalizada de login

        camelo_id = self.kwargs.get("camelo_id")
        camelo = get_object_or_404(Camelo, id=camelo_id)

        usuario = self.request.user

        valido = Camelo_Usuario.objects.filter(camelo=camelo, usuario=usuario).exists()

        if not valido:
             return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        campo_escolhido = self.request.GET.get('campo')
        valor = self.request.GET.get(campo_escolhido)  # valor digitado no input

        camelo_id = self.kwargs.get("camelo_id")
        camelo = get_object_or_404(Camelo, id=camelo_id)

        perfis = Camelo_Usuario.objects.filter(camelo=camelo)

        if valor is None:
            perfis = Camelo_Usuario.objects.filter(camelo=camelo)
        else:
            filtro = {f"{campo_escolhido}__icontains": valor}
            perfis = Perfil.objects.filter(**filtro)

        
        return perfis
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        campos = [
            (field.name, field.verbose_name.title() if field.verbose_name else field.name.title())
            for field in self.model._meta.fields
            if field.name != 'usuario'
        ]

        campos.append(('usuario__email', 'Email do Usuário'))

        camelo_id = self.kwargs.get("camelo_id")
        camelo = get_object_or_404(Camelo, id=camelo_id)



        campo_escolhido = self.request.GET.get('campo')
        
        context['campo_escolhido'] = campo_escolhido
        context['campos'] = campos
        context['nome_modelo_lista'] = 'usuarios'
        context['camelo'] = camelo
        return context



class SobreView(TemplateView):
    template_name = "paginas/rodape/sobre.html"


class ContatoView(TemplateView):
    template_name = "paginas/rodape/contato.html"


class PrivacidadeView(TemplateView):
    template_name = "paginas/rodape/privacidade.html"

class AjudaView(TemplateView):
    template_name = "paginas/rodape/ajuda.html"
