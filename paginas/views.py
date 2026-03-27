from django.views.generic import TemplateView



from cadastros.views import Produto, Carrinho_Produto, Carrinho, Camelo, Pedido_Produto

from cadastros.models import Produto, Avaliacao, Camelo, Camelo_Usuario, Pedido, Pedido_Produto
from cadastros.forms import AvaliacaoForm

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View

from django.shortcuts import get_object_or_404, redirect, render

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
# Create your views here.


class IndexView(TemplateView):
    template_name = "paginas/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 1. Buscamos os produtos usando o Manager que criamos
        melhores_produtos_qs = Produto.objects.melhores_avaliados().annotate(
            qtd_total_avaliacoes=Count('avaliacoes')
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
                # Se você não tiver esse campo no model, use o annotate do Manager
                'qtd_avaliacoes': produto.qtd_total_avaliacoes, 
            })

        # 3. Enviamos para o contexto
        context['melhores_produtos'] = lista_customizada
        context['camelos'] = Camelo.objects.all()
        
        return context

class EmailConfirmacaoView(TemplateView):
    template_name = "paginas/confirmar.html"


class CameloView(TemplateView):
    template_name = "paginas/camelo_padrao.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        camelo_id = self.kwargs.get("pk")
        camelo = get_object_or_404(Camelo, pk=camelo_id)
        context["camelo"] = camelo
        return context


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
        queryset = Produto.objects.annotate(qtd_total_avaliacoes=Count('avaliacoes'))

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

    
    def get_queryset(self):
        self.object_list = Camelo.objects.filter()

        txt_nome = self.request.GET.get('nome_fantasia')

        if txt_nome:
            self.object_list = Camelo.objects.filter(nome_fantasia__icontains=txt_nome)
        else:
            self.object_list = Camelo.objects.filter()

        return self.object_list


class ClienteProdutoCameloList(ListView):


    model = Produto
    template_name = 'paginas/camelo/produtos-camelo.html'
    context_object_name = 'produtos'

    
    def get_queryset(self):

        camelo_id = self.kwargs.get("pk")
        queryset = Produto.objects.annotate(qtd_total_avaliacoes=Count('avaliacoes'))

        txt_nome = self.request.GET.get('nome')

        if txt_nome:
            queryset = queryset.filter(nome__icontains=txt_nome, camelo_id=camelo_id)

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

        ja_avaliou = Avaliacao.objects.filter(produto=produto, usuario=usuario)


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

        pedidos_andamento = Pedido.objects.filter(usuario=self.request.user, status='em andamento')
        pedidos_finalizado = Pedido.objects.filter(usuario=self.request.user, status='finalizado')
        pedidos_cancelado = Pedido.objects.filter(usuario=self.request.user, status='cancelado')

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
                        status="em andamento",
                        opcao_pedido=dados.get('opcao_pedido', 'casa'),
                        endereco=endereco
                    )

                    # 3. Loop nos itens do carrinho criando Pedido_Produto para cada um
                    for item in carrinho.produtos.all():
                        Pedido_Produto.objects.create(
                            pedido=pedido,
                            produto=item.produto,
                            quantidade=item.quantidade,
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
                        status="em andamento",
                        opcao_pedido=dados['opcao_pedido'],
                        endereco=endereco
                    )

                    Pedido_Produto.objects.create(
                        pedido=pedido,
                        produto=produto,
                        quantidade=quantidade,
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
  
