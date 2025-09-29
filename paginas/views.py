from django.views.generic import TemplateView

from cadastros.views import Produto
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

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


class VerCarrinho(TemplateView):
    template_name = 'paginas/ver_carrinho.html'
