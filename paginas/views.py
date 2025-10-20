from django.views.generic import TemplateView

from cadastros.views import Produto, Carrinho_Produto, Carrinho
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View

from django.shortcuts import get_object_or_404, redirect

from django.http import JsonResponse
# Create your views here.


class IndexView(TemplateView):
    template_name = "paginas/index.html"


class AcessoNegadoView(TemplateView):
    template_name = 'paginas/acesso_negado.html'



class ClienteProdutoList(ListView):


    model = Produto
    template_name = 'paginas/produtos.html'

    
    def get_queryset(self):
        self.object_list = Produto.objects.filter()

        txt_nome = self.request.GET.get('nome')

        if txt_nome:
            self.object_list = Produto.objects.filter(nome__icontains=txt_nome)
        else:
            self.object_list = Produto.objects.filter()

        return self.object_list
    
class ProdutoEspecifico(DetailView):
    model = Produto
    template_name = 'paginas/produto.html'


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
        total = sum(item.produto.preco * item.quantidade for item in context['itens'])
        context['total'] = total
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

    carrinho = item.carrinho
    total = sum(prod.produto.preco * prod.quantidade for prod in Carrinho_Produto.objects.filter(carrinho=item.carrinho))


    return JsonResponse({'quantidade': item.quantidade,
                        'total': f'{total:.2f}'.replace('.', ',')
                    })