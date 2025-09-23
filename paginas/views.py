from django.views.generic import TemplateView

from cadastros.views import Produto
from django.views.generic.list import ListView

# Create your views here.


class IndexView(TemplateView):
    template_name = "paginas/index.html"


class AcessoNegadoView(TemplateView):
    template_name = 'paginas/acesso_negado.html'



class ClienteProdutoList(ListView):


    model = Produto
    template_name = 'paginas/produtos.html'

    # def dispatch(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return redirect('login')  # ou sua URL personalizada de login
    #     if not request.user.groups.filter(name='administrador').exists():
    #         return redirect('acesso-negado')  # ou 'acesso-negado'
    #     return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        campo_escolhido = self.request.GET.get('campo')
        valor = self.request.GET.get(campo_escolhido)  # valor digitado no input

        if valor is None:
            produtos = Produto.objects.all()
        else:
            filtro = {f"{campo_escolhido}__icontains": valor}
            produtos = Produto.objects.filter(**filtro)

        
        return produtos
    

    # def get_context_data(self, **kwargs):

    #     context = super().get_context_data(**kwargs)
    #     campos = [field.name for field in self.model._meta.fields]
        
    #     campo_escolhido = self.request.GET.get('campo')
        

    #     context['campo_escolhido'] = campo_escolhido
    #     context['campos'] = campos
    #     context['nome_modelo_lista'] = 'produtos'
    #     return context