from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import Categoria

from usuarios.models import Perfil


from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin

from django.shortcuts import get_object_or_404

from django.shortcuts import redirect


# Create your views here.

# Create
class CategoriaCreate(GroupRequiredMixin, LoginRequiredMixin, CreateView):

    group_required = u"administrador"

    model = Categoria
    fields = ['nome', 'descricao']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('cadastrar-categoria')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)


# Update
class CategoriaUpdate(GroupRequiredMixin, LoginRequiredMixin, UpdateView):

    group_required = u"administrador"

    model = Categoria
    fields = ['nome', 'descricao']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('listar-categorias')


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)




# List
class CategoriaList(GroupRequiredMixin, LoginRequiredMixin, ListView):

    group_required = u"administrador"

    model = Categoria
    template_name = 'cadastros/listas/categoria.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)


class PerfilList(GroupRequiredMixin, LoginRequiredMixin, ListView):

    group_required = u"administrador"

    model = Perfil
    template_name = 'cadastros/listas/perfil.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)
