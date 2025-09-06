from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import Categoria

from usuarios.models import Perfil


from django.urls import reverse_lazy

# Create your views here.

# Create
class CategoriaCreate(CreateView):

    model = Categoria
    fields = ['nome', 'descricao']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('cadastrar-categoria')







# List
class CategoriaList(ListView):
    model = Categoria
    template_name = 'cadastros/listas/categoria.html'

class PerfilList(ListView):
    model = Perfil
    template_name = 'cadastros/listas/perfil.html'