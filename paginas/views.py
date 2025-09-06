from django.views.generic import TemplateView

# Create your views here.


class IndexView(TemplateView):
    template_name = "paginas/index.html"


class AcessoNegadoView(TemplateView):
    template_name = 'paginas/acesso_negado.html'
