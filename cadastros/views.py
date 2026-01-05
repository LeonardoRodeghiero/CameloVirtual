from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views import View

from .models import Categoria, Produto, Carrinho, Carrinho_Produto, Camelo, Camelo_Usuario

from usuarios.models import Perfil


from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin

from django.shortcuts import get_object_or_404

from django.shortcuts import redirect

from django.db.models import CharField, TextField

from django.utils import timezone

from datetime import datetime

from django.db.models import Sum, F, ExpressionWrapper, DecimalField
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
        context['titulo_botao'] = "Cadastrar"
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
        context['titulo_botao'] = "Cadastrar"

        return context

class CarrinhoCreate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Cria o carrinho se não existir
        Carrinho.objects.get_or_create(usuario=request.user)

        produto_id = kwargs['produto_id']
        return redirect('adicionar-produto-carrinho', produto_id=produto_id)
    
class CarrinhoProdutoCreate(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        produto = get_object_or_404(Produto, id=kwargs['produto_id'])
        carrinho, _ = Carrinho.objects.get_or_create(usuario=request.user)

        quantidade = int(request.POST.get('quantidade', 1))

        item, criado = Carrinho_Produto.objects.get_or_create(
            carrinho=carrinho,
            produto=produto,
            defaults={'quantidade': quantidade}
        )

        if not criado:
            item.quantidade += quantidade
            item.save()

        Carrinho.objects.filter(id=carrinho.id).update(atualizado_em=timezone.now())
        return redirect('ver-carrinho')

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
        

        Carrinho.objects.filter(id=carrinho.id).update(atualizado_em=timezone.now())
        return redirect('ver-carrinho')

class CameloCreate(LoginRequiredMixin, CreateView):


    model = Camelo
    fields = ['nome_fantasia', 'cnpj', 'email', 'telefone', 'descricao_loja', 'imagem_logo', 'endereco']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('index')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo_form'] = "Cadastre Seu Camelô"
        context['titulo_botao'] = "Cadastrar"

        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        # adiciona o usuário logado como administrador
        Camelo_Usuario.objects.create(
            camelo=self.object,
            usuario=self.request.user
        )
        return response



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
        context['titulo_botao'] = "Atualizar"

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
        context['titulo_botao'] = "Atualizar"

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

class CarrinhoDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):

    login_url = reverse_lazy('login')

    group_required = u"administrador"

    model = Carrinho
    success_url = reverse_lazy('listar-carrinhos')


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)

class CameloDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):

    login_url = reverse_lazy('login')

    group_required = u"administrador"

    model = Camelo
    success_url = reverse_lazy('listar-camelos')


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)


class CarrinhoDeleteUser(LoginRequiredMixin, DeleteView):

    login_url = reverse_lazy('login')

    model = Carrinho
    success_url = reverse_lazy('index')



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


        campos = [
            (field.name, field.verbose_name.title() if field.verbose_name else field.name.title())
            for field in self.model._meta.fields
        ]


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
        campos = [
            (field.name, field.verbose_name.title() if field.verbose_name else field.name.title())
            for field in self.model._meta.fields
            if field.name != 'usuario'
        ]

        campos.append(('usuario__email', 'Email do Usuário'))

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

    foreign_key_map = {
            'categoria': 'nome',
        }

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
            return Produto.objects.all()


        field = Produto._meta.get_field(campo_escolhido)
        if field.get_internal_type() == "ForeignKey":
            filtro = {f"{campo_escolhido}__nome__icontains": valor}

        else:
            filtro = {f"{campo_escolhido}__icontains": valor}

        
        return Produto.objects.filter(**filtro)

    

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        campos = [
            (field.name, field.verbose_name.title() if field.verbose_name else field.name.title())
            for field in self.model._meta.fields
            if field.name != 'imagem'
        ]
        campo_escolhido = self.request.GET.get('campo')
        

        context['campo_escolhido'] = campo_escolhido
        context['campos'] = campos
        context['nome_modelo_lista'] = 'produtos'
        return context


class CarrinhoList(GroupRequiredMixin, LoginRequiredMixin, ListView):

    group_required = u"administrador"

    model = Carrinho
    template_name = 'cadastros/listas/carrinho.html'

    foreign_key_map = {
            'usuario': 'username',
        }
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

        qs = Carrinho.objects.all()

        if campo_escolhido == "valorTotal" and valor:
            qs = qs.annotate(
                valor_total=Sum(
                    F("produtos__quantidade") * F("produtos__produto__preco"),
                    output_field=DecimalField()
                )
            ).filter(valor_total__icontains=valor)
            return qs

        if valor is None:
            return Carrinho.objects.all()
        
        if campo_escolhido.startswith("produtos__"):
            filtro = {f"{campo_escolhido}__icontains": valor}
            return Carrinho.objects.filter(**filtro).distinct()

        field = Carrinho._meta.get_field(campo_escolhido)
        if field.get_internal_type() == "ForeignKey":
            filtro = {f"{campo_escolhido}__username__icontains": valor}
        
        elif field.get_internal_type() in ["DateTimeField", "DateField"]:
            try:
                # tenta DD/MM/AAAA
                data = datetime.strptime(valor, "%d/%m/%Y").date()
                if field.get_internal_type() == "DateTimeField":
                    inicio = datetime.combine(data, datetime.min.time())
                    fim = datetime.combine(data, datetime.max.time())
                    filtro = {f"{campo_escolhido}__range": (inicio, fim)}
                else:
                    filtro = {campo_escolhido: data}

            except ValueError:
                try:
                    # tenta DD/MM (sem ano)
                    data = datetime.strptime(valor, "%d/%m")
                    filtro = {
                        f"{campo_escolhido}__day": data.day,
                        f"{campo_escolhido}__month": data.month,
                    }
                except ValueError:
                    return Carrinho.objects.all()
        else:
            filtro = {f"{campo_escolhido}__icontains": valor}

        
        return Carrinho.objects.filter(**filtro)
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        campos_carrinho = [
            (field.name, field.verbose_name.title() if field.verbose_name else field.name.title())
            for field in self.model._meta.fields
        ]

        campos_produto = [
            ("produtos__produto__nome", "Nome do Produto"),
            ("produtos__quantidade", "Quantidade"),
        ]

        campos_extra = [
            ("valorTotal", "Valor Total"),
        ]


        campo_escolhido = self.request.GET.get('campo')
        
        context['campo_escolhido'] = campo_escolhido
        context['campos'] = campos_carrinho + campos_produto + campos_extra
        context['nome_modelo_lista'] = 'carrinhos'
        return context



class CameloList(GroupRequiredMixin, LoginRequiredMixin, ListView):

    group_required = u"administrador"

    model = Camelo
    template_name = 'cadastros/listas/camelo.html'

    foreign_key_map = {
            'usuario': 'username',
        }
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
            return Camelo.objects.all()
        
        if campo_escolhido and campo_escolhido.startswith("usuarios__"):
            filtro = {f"{campo_escolhido}__icontains": valor}
            return Camelo.objects.filter(**filtro).distinct()

        field = Camelo._meta.get_field(campo_escolhido)
        if field.get_internal_type() == "ForeignKey":
            filtro = {f"{campo_escolhido}__username__icontains": valor}
        
        elif field.get_internal_type() in ["DateTimeField", "DateField"]:
            try:
                # tenta DD/MM/AAAA
                data = datetime.strptime(valor, "%d/%m/%Y").date()
                if field.get_internal_type() == "DateTimeField":
                    inicio = datetime.combine(data, datetime.min.time())
                    fim = datetime.combine(data, datetime.max.time())
                    filtro = {f"{campo_escolhido}__range": (inicio, fim)}
                else:
                    filtro = {campo_escolhido: data}

            except ValueError:
                try:
                    # tenta DD/MM (sem ano)
                    data = datetime.strptime(valor, "%d/%m")
                    filtro = {
                        f"{campo_escolhido}__day": data.day,
                        f"{campo_escolhido}__month": data.month,
                    }
                except ValueError:
                    return Camelo.objects.all()
        else:
            filtro = {f"{campo_escolhido}__icontains": valor}

        
        return Camelo.objects.filter(**filtro)
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        campos_camelo = [
            (field.name, field.verbose_name.title() if field.verbose_name else field.name.title())
            for field in self.model._meta.fields
        ]

        campos_usuario = [
            ("usuarios__username", "Nome Completo do Usuário"),
            ("usuarios_cpf", "CPF do Usuário"),
        ]


        


        campo_escolhido = self.request.GET.get('campo')
        
        context['campo_escolhido'] = campo_escolhido
        context['campos'] = campos_camelo + campos_usuario
        context['nome_modelo_lista'] = 'camelos'
        return context
