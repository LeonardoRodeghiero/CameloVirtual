from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views import View

from .models import Categoria, Produto, Carrinho, Carrinho_Produto

from usuarios.models import Perfil


from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin

from django.shortcuts import get_object_or_404

from django.shortcuts import redirect

from django.db.models import CharField, TextField
# Create your views here.

# Create
class CategoriaCreate(GroupRequiredMixin, LoginRequiredMixin, CreateView):

    group_required = u"administrador"

    model = Categoria
    fields = ['nome', 'descricao']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('listar-categorias')


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo_form'] = "Cadastre a Categoria"
        return context

class ProdutoCreate(GroupRequiredMixin, LoginRequiredMixin, CreateView):

    group_required = u"administrador"

    model = Produto
    fields = ['nome', 'marca', 'descricao', 'preco', 'quantidade', 'imagem', 'categoria']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('listar-produtos')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo_form'] = "Cadastre o Produto"
        return context

class CarrinhoCreate(View):
    def get(self, request, *args, **kwargs):
        # Cria o carrinho se não existir
        Carrinho.objects.get_or_create(usuario=request.user)

        produto_id = kwargs['produto_id']
        return redirect('adicionar-produto-carrinho', produto_id=produto_id)
    
class CarrinhoProdutoCreate(View):
    def get(self, request, *args, **kwargs):
        produto = get_object_or_404(Produto, id=kwargs['produto_id'])
        carrinho = Carrinho.objects.get(usuario=request.user)

        item, criado = Carrinho_Produto.objects.get_or_create(
            carrinho=carrinho,
            produto=produto,
            defaults={'quantidade': 1}
        )

        if not criado:
            item.quantidade += 1
            item.save()
        
        return redirect('ver-carrinho')

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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo_form'] = "Edite a Categoria"
        return context

class ProdutoUpdate(GroupRequiredMixin, LoginRequiredMixin, UpdateView):

    group_required = u"administrador"

    model = Produto
    fields = ['nome', 'marca', 'descricao', 'preco', 'quantidade', 'imagem', 'categoria']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('listar-produtos')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo_form'] = "Edite o Produto"
        return context
# Delete

class CategoriaDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):

    login_url = reverse_lazy('login')

    group_required = u"administrador"

    model = Categoria
    success_url = reverse_lazy('listar-categorias')


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)

class ProdutoDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):

    login_url = reverse_lazy('login')

    group_required = u"administrador"

    model = Produto
    success_url = reverse_lazy('listar-produtos')


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

    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        campo_escolhido = self.request.GET.get('campo')
        valor = self.request.GET.get(campo_escolhido)  # valor digitado no input

        if valor is None:
            categorias = Categoria.objects.all()
        else:
            filtro = {f"{campo_escolhido}__icontains": valor}
            categorias = Categoria.objects.filter(**filtro)

        
        return categorias



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        campos = [field.name for field in self.model._meta.fields]

        campo_escolhido = self.request.GET.get('campo')
        
        context['campo_escolhido'] = campo_escolhido
        context['campos'] = campos
        context['nome_modelo_lista'] = 'categorias'
        return context



class PerfilList(GroupRequiredMixin, LoginRequiredMixin, ListView):

    group_required = u"administrador"

    model = Perfil
    template_name = 'cadastros/listas/perfil.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        campo_escolhido = self.request.GET.get('campo')
        valor = self.request.GET.get(campo_escolhido)  # valor digitado no input

        if valor is None:
            perfis = Perfil.objects.all()
        else:
            filtro = {f"{campo_escolhido}__icontains": valor}
            perfis = Perfil.objects.filter(**filtro)

        
        return perfis
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        campos = [field.name for field in self.model._meta.fields]


        campo_escolhido = self.request.GET.get('campo')
        
        context['campo_escolhido'] = campo_escolhido
        context['campos'] = campos
        context['nome_modelo_lista'] = 'usuarios'
        return context

class ProdutoList(GroupRequiredMixin, LoginRequiredMixin, ListView):

    group_required = u"administrador"

    model = Produto
    template_name = 'cadastros/listas/produto.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        campo_escolhido = self.request.GET.get('campo')
        valor = self.request.GET.get(campo_escolhido)  # valor digitado no input

        if valor is None:
            produtos = Produto.objects.all()
        else:
            filtro = {f"{campo_escolhido}__icontains": valor}
            produtos = Produto.objects.filter(**filtro)

        
        return produtos
    

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        campos = [field.name for field in self.model._meta.fields]
        
        campo_escolhido = self.request.GET.get('campo')
        

        context['campo_escolhido'] = campo_escolhido
        context['campos'] = campos
        context['nome_modelo_lista'] = 'produtos'
        return context