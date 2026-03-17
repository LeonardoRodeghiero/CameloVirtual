from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views import View

from .models import Categoria, Produto, Carrinho, Carrinho_Produto, Camelo, Camelo_Usuario, Pedido, Pedido_Produto, Avaliacao

from .forms import AvaliacaoForm, PedidoForm

from .forms import (
    CameloIdentificacaoForm,
    CameloContatoForm,
    CameloPerfilForm,
    CameloEnderecoForm,
)

from .forms import (
    ProdutoInformacaoForm,
    ProdutoDetalhesForm,
    ProdutoImagemForm,
    ProdutoFornecedorForm,
)

from usuarios.models import Perfil


from django.urls import resolve, Resolver404, reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin

from django.shortcuts import get_object_or_404

from django.shortcuts import redirect, render

from django.db.models import CharField, TextField

from django.utils import timezone

from datetime import datetime

from django.db.models import Sum, F, ExpressionWrapper, DecimalField

from django.core.exceptions import ValidationError

from django.db.models import Q

from formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage

file_storage = FileSystemStorage(location='/tmp/wizard')



# Create your views here.

# Create
class CategoriaCreate(LoginRequiredMixin, CreateView):

    model = Categoria
    fields = ['nome', 'descricao']
    template_name = 'cadastros/form.html'

    def get_success_url(self):
        return reverse_lazy('listar-categorias-camelo', kwargs={'pk': self.kwargs.get("pk")})



    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        camelo_id = self.kwargs.get("pk") 
        if camelo_id: 
            context["base_template"] = "paginas/camelo_padrao.html" 
        else: 
            context["base_template"] = "paginas/index.html"

        camelo_id = self.kwargs.get("pk") 
        camelo = get_object_or_404(Camelo, pk=camelo_id) 
        context["camelo"] = camelo

        context['titulo_form'] = "Cadastre a Categoria"
        context['titulo_botao'] = "Cadastrar"
        return context

    def form_valid(self, form): 
        camelo_id = self.kwargs.get("pk") # pega o id da URL 
        form.instance.camelo_id = camelo_id # vincula ao modelo 
        return super().form_valid(form)


    
class ProdutoCreate(LoginRequiredMixin, CreateView):


    model = Produto
    fields = ['nome', 'marca', 'descricao', 'preco', 'quantidade', 'imagem', 'categoria']
    template_name = 'cadastros/form.html'
    
    def get_success_url(self):
        return reverse_lazy('listar-produtos-camelo', kwargs={'pk': self.kwargs.get("pk")})

    def get_form(self, form_class=None): 
        form = super().get_form(form_class) 
        camelo_id = self.kwargs.get("pk") # id do camelô vindo da URL 
        if camelo_id: 
            form.fields['categoria'].queryset = Categoria.objects.filter(camelo_id=camelo_id) 
        return form


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        camelo_id = self.kwargs.get("pk") 
        if camelo_id: 
            context["base_template"] = "paginas/camelo_padrao.html" 
        else: 
            context["base_template"] = "paginas/index.html"

        camelo_id = self.kwargs.get("pk") 
        camelo = get_object_or_404(Camelo, pk=camelo_id) 
        context["camelo"] = camelo


        context['titulo_form'] = "Cadastre o Produto"
        context['titulo_botao'] = "Cadastrar"

        return context

    def form_valid(self, form): 
        camelo_id = self.kwargs.get("pk") # pega o id da URL 
        form.instance.camelo_id = camelo_id # vincula ao modelo 
        return super().form_valid(form)

class ProdutoCreateWizard(SessionWizardView):
    form_list = [
        ProdutoInformacaoForm,
        ProdutoDetalhesForm,
        ProdutoImagemForm,
        ProdutoFornecedorForm,
    ]
    template_name = "cadastros/form.html"
    file_storage = file_storage


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        camelo_id = self.kwargs.get("pk") 
        if camelo_id: 
            context["base_template"] = "paginas/camelo_padrao.html" 
        else: 
            context["base_template"] = "paginas/index.html"

        camelo = get_object_or_404(Camelo, pk=camelo_id) 
        context["camelo"] = camelo
        
        titulos = {
            '0': "Preencha as informações do produto",
            '1': "Preencha os detalhes do produto",
            '2': "Defina a imagem do produto",
            '3': "Informe o fornecedor do produto",
        }

        # pega o step atual e define o título
        step_atual = self.steps.current
        context['titulo_form'] = titulos.get(step_atual, "Crie seu camelô")

        # botão muda conforme etapa
        context['titulo_botao'] = (
            "Criar" if step_atual == self.steps.last else "Próximo"
        )


        current = int(self.steps.step1)
        total = self.steps.count
        progress_percent = int((current / total) * 100)

        # pega o step anterior (se não for o primeiro)
        previous = current - 1 if current > 1 else 0
        previous_percent = int((previous / total) * 100)

        context['progress_percent'] = progress_percent
        context['previous_percent'] = previous_percent
        context['progress_text'] = f"Etapa {current} de {total}"




        return context

    # def get_form_kwargs(self, step=None):
    #     kwargs = super().get_form_kwargs(step)
    #     kwargs['camelo'] = self.request.user.camelos.all()
    #     return kwargs

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        camelo_id = self.kwargs.get("pk")
        if camelo_id:
            kwargs['camelo_id'] = camelo_id
        return kwargs


    def done(self, form_list, **kwargs):
        informacao = form_list[0].cleaned_data
        detalhes = form_list[1].cleaned_data
        imagem = form_list[2].cleaned_data
        fornecedor = form_list[3].cleaned_data

        cadastro = Produto.objects.create(
            nome=informacao['nome'],
            marca=informacao['marca'],
            categoria=informacao['categoria'],

            descricao=detalhes['descricao'],
            preco=detalhes['preco'],
            quantidade=detalhes['quantidade'],
            imagem=imagem['imagemfornecedor'],
            fornecedor=fornecedor['fornecedor'],
        )
        


        return reverse_lazy('listar-produtos-camelo', kwargs={'pk': self.kwargs.get("pk")})



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
    # success_url = reverse_lazy('camelo', kwargs={'pk': self.kwargs.get("pk")})

    def get_success_url(self):
        return reverse_lazy('camelo', kwargs={'pk': self.object.pk})

    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo_form'] = "Cadastre Seu Camelô"
        context['titulo_botao'] = "Cadastrar"

        return context


    @staticmethod
    def validar_cnpj(value):
        if len(value) != 18:
            raise ValidationError("CNPJ deve ter 18 dígitos.")

        cnpj = ''.join(filter(str.isdigit, value))

        pesos1 = [5,4,3,2,9,8,7,6,5,4,3,2]
        pesos2 = [6] + pesos1

        def calcular_digito(cnpj, pesos):
            soma = sum(int(digito) * peso for digito, peso in zip(cnpj, pesos))
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)

        digito1 = calcular_digito(cnpj[:12], pesos1)
        digito2 = calcular_digito(cnpj[:12] + digito1, pesos2)

        if cnpj[-2:] != digito1 + digito2:
            raise ValidationError("CNPJ inválido.")



    def form_valid(self, form):

        # try: 
        #     self.validar_cnpj(form.cleaned_data['cnpj']) 
        # except ValidationError as e: 
        #     form.add_error('cnpj', e) 
        #     return self.form_invalid(form)


        response = super().form_valid(form)
        # adiciona o usuário logado como administrador
        Camelo_Usuario.objects.create(
            camelo=self.object,
            usuario=self.request.user
        )
        return response

class CameloCreateWizard(SessionWizardView):
    form_list = [
        CameloIdentificacaoForm,
        CameloContatoForm,
        CameloPerfilForm,
        CameloEnderecoForm,
    ]
    template_name = "cadastros/form.html"
    file_storage = file_storage


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        titulos = {
            '0': "Preencha a identificação do Camelô",
            '1': "Preencha os dados para contato",
            '2': "Defina o perfil do camelô",
            '3': "Informe o endereço do camelô",
        }

        # pega o step atual e define o título
        step_atual = self.steps.current
        context['titulo_form'] = titulos.get(step_atual, "Crie seu camelô")

        # botão muda conforme etapa
        context['titulo_botao'] = (
            "Criar" if step_atual == self.steps.last else "Próximo"
        )


        current = int(self.steps.step1)
        total = self.steps.count
        progress_percent = int((current / total) * 100)

        # pega o step anterior (se não for o primeiro)
        previous = current - 1 if current > 1 else 0
        previous_percent = int((previous / total) * 100)

        context['progress_percent'] = progress_percent
        context['previous_percent'] = previous_percent
        context['progress_text'] = f"Etapa {current} de {total}"




        return context

    def done(self, form_list, **kwargs):
        identificacao = form_list[0].cleaned_data
        contato = form_list[1].cleaned_data
        perfil = form_list[2].cleaned_data
        endereco = form_list[3].cleaned_data

        cadastro = Camelo.objects.create(
            nome_fantasia=identificacao['nome_fantasia'],
            cnpj=identificacao['cnpj'],
            email=contato['email'],
            telefone=contato['telefone'],
            descricao_loja=perfil['descricao_loja'],
            imagem_logo=perfil['imagem_logo'],
            estado=endereco['estado'],
            cidade=endereco['cidade'],
            bairro=endereco.get('bairro'),
            logradouro=endereco.get('logradouro'),
            numero=endereco.get('numero'),
            complemento=endereco.get('complemento'),
            cep=endereco.get('cep'),
        )
        Camelo_Usuario.objects.create(
            camelo=cadastro,
            usuario=self.request.user
        )





        # cadastro.gerar_codigo()
        # cadastro.gerar_codigo_sms()

        # send_mail(
        #     "Confirmação de cadastro",
        #     f"Seu código é {cadastro.codigo}",
        #     "rodeghieroleonardo@gmail.com",
        #     [cadastro.email]
        # )

        # telefone = "+55" + ''.join(filter(str.isdigit, cadastro.telefone))
        # client = Client(config("TWILIO_SID"), config("TWILIO_AUTH_TOKEN"))
        # client.messages.create(
        #     body=f"Seu código de telefone é {cadastro.codigo_sms}",
        #     from_=config("TWILIO_NUMBER"),
        #     to=telefone
        # )

        # return redirect("confirmar-codigo", email=cadastro.email)
        return redirect("index")




class PedidoCarrinho(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


    def post(self, request, *args, **kwargs):
        carrinho = get_object_or_404(Carrinho, usuario=request.user)

        if not carrinho.produtos.exists():
            return redirect('ver-carrinho')

        total = sum(item.produto.preco * item.quantidade for item in carrinho.produtos.all())

        pedido = Pedido.objects.create(
            usuario=request.user,
            valor_total=total, 
            data_pedido=timezone.now(),
            status="em andamento"
        )

        for item in carrinho.produtos.all():
            Pedido_Produto.objects.create(
                pedido=pedido,
                produto=item.produto,
                quantidade=item.quantidade,
                preco_unitario=item.produto.preco
            )

        
        carrinho.produtos.all().delete()

        return redirect('index')
        
class PedidoProdutoDireto(View):
    def get(self, request, *args, **kwargs):
        form = PedidoForm()
        produto = get_object_or_404(Produto, id=kwargs['produto_id'])
        return render(request, "paginas/produto.html", {"produto": produto, "form": form})

    
    def post(self, request, *args, **kwargs):
        produto = get_object_or_404(Produto, id=kwargs['produto_id'])
        try:
            quantidade = int(request.POST.get('quantidade', 1))
        except ValueError:
            quantidade = 1
        opcao_pedido = request.POST.get('entrega')  # pega direto do POST
        print(opcao_pedido)
        
        if opcao_pedido == "casa":
            # redireciona para página de endereço, passando dados via sessão
            request.session['pedido_temp'] = {
                'produto_id': produto.id,
                'quantidade': quantidade,
                'opcao_pedido': opcao_pedido
            }
            return redirect("confirmar-endereco")
        else:
            pedido = Pedido.objects.create(
                usuario=request.user,
                valor_total=produto.preco * quantidade,
                data_pedido=timezone.now(),
                status="em andamento",
                opcao_pedido=opcao_pedido

            )

            Pedido_Produto.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=produto.preco
            )

            return redirect('index')


# class AvaliacaoCreate(LoginRequiredMixin, View):
#     def get(self, request, produto_id):
#         form = AvaliacaoForm()
#         return render(request, 'produto.html', {'form': form})

#     def post(self, request, produto_id):
#         form = AvaliacaoForm(request.POST)
#         if form.is_valid():
#             avaliacao = form.save(commit=False)
#             avaliacao.usuario = request.user
#             avaliacao.produto_id = produto_id
#             avaliacao.save()
#             return render('produto_detail', pk=produto_id)
#         return render(request, 'produto.html', {'form': form})

# Update
class CategoriaUpdate(GroupRequiredMixin, LoginRequiredMixin, UpdateView):

    group_required = u"administrador"

    model = Categoria
    fields = ['nome', 'descricao']
    template_name = 'cadastros/form.html'

    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            try:
                match = resolve(next_url)
                if match.url_name == "listar-categorias":
                    return reverse_lazy("listar-categorias")
                if match.url_name == "listar-categorias-camelo":
                    return reverse_lazy("listar-categorias-camelo", kwargs={"pk": match.kwargs.get("pk")})
            except Resolver404:
                pass
        # fallback global
        return reverse_lazy("listar-categorias")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_url = self.request.GET.get("next") or self.request.POST.get("next")

        categoria = self.object # objeto que está sendo editado 
        camelo = getattr(categoria, "camelo", None)

        if next_url and next_url.strip("/").split("/")[0].isdigit():
            context["base_template"] = "paginas/camelo_padrao.html"
            context["camelo"] = camelo
        else:
            context["base_template"] = "paginas/index.html"

        context['titulo_form'] = "Edite a Categoria"
        context['titulo_botao'] = "Atualizar"
        return context








class ProdutoUpdate(GroupRequiredMixin, LoginRequiredMixin, UpdateView):

    group_required = u"administrador"

    model = Produto
    fields = ['nome', 'marca', 'descricao', 'preco', 'quantidade', 'imagem', 'categoria']
    template_name = 'cadastros/form.html'

    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            try:
                match = resolve(next_url)
                if match.url_name == "listar-produtos":
                    return reverse_lazy("listar-produtos")
                if match.url_name == "listar-produtos-camelo":
                    return reverse_lazy("listar-produtos-camelo", kwargs={"pk": match.kwargs.get("pk")})
            except Resolver404:
                pass
        # fallback global
        return reverse_lazy("listar-produtos")

    def get_form(self, form_class=None): 
        form = super().get_form(form_class) 
        camelo = self.object.camelo # pega o camelô do produto 
        form.fields['categoria'].queryset = Categoria.objects.filter(camelo=camelo) 
        return form


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        next_url = self.request.GET.get("next") or self.request.POST.get("next")

        produto = self.object # objeto que está sendo editado 
        camelo = getattr(produto, "camelo", None)

        if next_url and next_url.strip("/").split("/")[0].isdigit():
            context["base_template"] = "paginas/camelo_padrao.html"
            context["camelo"] = camelo
        else:
            context["base_template"] = "paginas/index.html"

        context['titulo_form'] = "Edite o Produto"
        context['titulo_botao'] = "Atualizar"
        return context



# Delete

class CategoriaDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):

    login_url = reverse_lazy('login')

    group_required = u"administrador"

    model = Categoria

    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            return next_url
        return reverse_lazy("listar-categorias")  # fallback global


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

    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            return next_url
        return reverse_lazy("listar-categorias")  # fallback global


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


class AvaliacaoDeleteUser(LoginRequiredMixin, DeleteView):

    login_url = reverse_lazy('login')

    model = Avaliacao

    def get_success_url(self):
        produto = self.object.produto  # pega o produto da avaliação que foi deletada
        return reverse_lazy('produto', kwargs={'pk': produto.pk})


class AvaliacaoDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):

    login_url = reverse_lazy('login')

    group_required = u"administrador"

    model = Avaliacao
    success_url = reverse_lazy('listar-avaliacoes')


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)


class PedidoDelete(GroupRequiredMixin, LoginRequiredMixin, DeleteView):

    login_url = reverse_lazy('login')

    group_required = u"administrador"

    model = Pedido
    success_url = reverse_lazy('listar-pedidos')


    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login
        if not request.user.groups.filter(name='administrador').exists():
            return redirect('acesso-negado')  # ou 'acesso-negado'
        return super().dispatch(request, *args, **kwargs)


class PedidoDeleteUser(LoginRequiredMixin, DeleteView):

    login_url = reverse_lazy('login')

    model = Pedido
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
            return Categoria.objects.all()


        field = Categoria._meta.get_field(campo_escolhido)
        if field.get_internal_type() == "ForeignKey":

            filtro = (
                Q(**{f"camelo__nome_fantasia__icontains": valor})
            )

        else:
            filtro = (
                Q(**{f"{campo_escolhido}__icontains": valor})
            )
        
        
        return Categoria.objects.filter(filtro)




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

class CategoriaCameloList(LoginRequiredMixin, ListView):

    model = Categoria
    template_name = 'cadastros/listas/camelos/categoria-camelo.html'

    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login

        camelo_id = kwargs.get('pk')
        camelo = get_object_or_404(Camelo, pk=camelo_id)

        if not camelo.usuarios.filter(id=request.user.id).exists():
            return redirect('acesso-negado-camelo', pk=camelo_id)


        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        camelo_id = self.kwargs.get("pk") # pega o id do camelô da URL
        campo_escolhido = self.request.GET.get('campo')
        valor = self.request.GET.get(campo_escolhido)  # valor digitado no input

        if valor is None:
            categorias = Categoria.objects.filter(camelo_id=camelo_id)
        else:
            filtro = {f"{campo_escolhido}__icontains": valor, "camelo_id": camelo_id}
            categorias = Categoria.objects.filter(**filtro)

        
        return categorias



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        campos = [
            (field.name, field.verbose_name.title() if field.verbose_name else field.name.title())
            for field in self.model._meta.fields
        ]

        camelo_id = self.kwargs.get("pk") 
        if camelo_id:
            campos = [(name, label) for name, label in campos if name != "camelo"] 
            camelo = get_object_or_404(Camelo, pk=camelo_id) 
            context["camelo"] = camelo


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
            filtro = (
                Q(**{f"categoria__nome__icontains": valor}) |
                Q(**{f"camelo__nome_fantasia__icontains": valor})
            )


        else:
            filtro = Q(**{f"{campo_escolhido}__icontains": valor})


        
        return Produto.objects.filter(filtro)

    

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


class ProdutoCameloList(LoginRequiredMixin, ListView):


    model = Produto
    template_name = 'cadastros/listas/camelos/produto-camelo.html'
    paginate_by = 10

    foreign_key_map = {
            'categoria': 'nome',
        }

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # ou sua URL personalizada de login

        camelo_id = kwargs.get('pk')
        camelo = get_object_or_404(Camelo, pk=camelo_id)

        if not camelo.usuarios.filter(id=request.user.id).exists():
            return redirect('acesso-negado-camelo', pk=camelo_id)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        camelo_id = self.kwargs.get("pk")  # pode ser None na lista geral
        campo_escolhido = self.request.GET.get('campo')
        valor = self.request.GET.get(campo_escolhido)

        # lista geral → sem pk → retorna tudo
        if camelo_id is None:
            qs = Produto.objects.all()
        else:
            qs = Produto.objects.filter(camelo_id=camelo_id)

        # se não tem valor, retorna tudo (já filtrado pelo camelô se houver pk)
        if not valor:
            return qs

        # aplica filtro de pesquisa
        field = Produto._meta.get_field(campo_escolhido)
        if field.get_internal_type() == "ForeignKey":
            qs = qs.filter(**{f"{campo_escolhido}__nome__icontains": valor})
        else:
            qs = qs.filter(**{f"{campo_escolhido}__icontains": valor})

        return qs


    

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        campos = [
            (field.name, field.verbose_name.title() if field.verbose_name else field.name.title())
            for field in self.model._meta.fields
            if field.name != 'imagem'
        ]
       
        camelo_id = self.kwargs.get("pk") 
        if camelo_id:
            campos = [(name, label) for name, label in campos if name != "camelo"] 
            camelo = get_object_or_404(Camelo, pk=camelo_id) 
            context["camelo"] = camelo



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
            filtro = (
                Q(**{f"usuarios__username__icontains": valor}) |
                Q(**{f"usuarios__perfil__cpf__icontains": valor})
            )
        
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
            filtro = Q(**{f"{campo_escolhido}__icontains": valor})


        
        return Camelo.objects.filter(filtro)
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        campos_camelo = [
            (field.name, field.verbose_name.title() if field.verbose_name else field.name.title())
            for field in self.model._meta.fields
            if field.name != 'imagem_logo'
        ]

        campos_usuario = [
            ("usuarios__username", "Nome Completo do Usuário"),
            ("usuarios__perfil__cpf", "CPF do Usuário"),
        ]


        


        campo_escolhido = self.request.GET.get('campo')
        
        context['campo_escolhido'] = campo_escolhido
        context['campos'] = campos_camelo + campos_usuario
        context['nome_modelo_lista'] = 'camelos'
        return context

class AvaliacaoList(GroupRequiredMixin, LoginRequiredMixin, ListView):

    group_required = u"administrador"

    model = Avaliacao
    template_name = 'cadastros/listas/avaliacao.html'

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
            return Avaliacao.objects.all()
        
        if campo_escolhido and campo_escolhido.startswith("usuarios__"):
            filtro = {f"{campo_escolhido}__icontains": valor}
            return Avaliacao.objects.filter(**filtro).distinct()

        field = Avaliacao._meta.get_field(campo_escolhido)
        if field.get_internal_type() == "ForeignKey":

            filtro = (
                Q(**{f"usuario__username__icontains": valor}) |
                Q(**{f"produto__nome__icontains": valor}) |
                Q(**{f"camelo__nome_fantasia__icontains": valor})
            )


        
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
                    return Avaliacao.objects.all()
        else:
            filtro = Q(**{f"{campo_escolhido}__icontains": valor})

        
        return Avaliacao.objects.filter(filtro)



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        campos = [
            (field.name, field.verbose_name.title() if field.verbose_name else field.name.title())
            for field in self.model._meta.fields
        ]


        campo_escolhido = self.request.GET.get('campo')
        
        context['campo_escolhido'] = campo_escolhido
        context['campos'] = campos
        context['nome_modelo_lista'] = 'avaliacoes'
        return context


class PedidoList(GroupRequiredMixin, LoginRequiredMixin, ListView):

    group_required = u"administrador"

    model = Pedido
    template_name = 'cadastros/listas/pedido.html'

    # foreign_key_map = {
    #         'usuario': 'username',
    #     }
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

        qs = Pedido.objects.all()

        # if campo_escolhido == "valorTotal" and valor:
        #     qs = qs.annotate(
        #         valor_total=Sum(
        #             F("produtos__quantidade") * F("produtos__produto__preco"),
        #             output_field=DecimalField()
        #         )
        #     ).filter(valor_total__icontains=valor)
        #     return qs

        if valor is None:
            return Pedido.objects.all()
        
        if campo_escolhido.startswith("produtos__"):
            filtro = {f"{campo_escolhido}__icontains": valor}
            return Pedido.objects.filter(**filtro).distinct()

        field = Pedido._meta.get_field(campo_escolhido)
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
                    return Pedido.objects.all()
        else:
            filtro = {f"{campo_escolhido}__icontains": valor}

        
        return Pedido.objects.filter(**filtro)
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        campos_pedido = [
            (field.name, field.verbose_name.title() if field.verbose_name else field.name.title())
            for field in self.model._meta.fields
        ]

        campos_produto = [
            ("produtos__produto__nome", "Nome do Produto"),
            ("produtos__quantidade", "Quantidade"),
        ]

        # campos_extra = [
        #     ("valorTotal", "Valor Total"),
        # ]


        campo_escolhido = self.request.GET.get('campo')
        
        context['campo_escolhido'] = campo_escolhido
        context['campos'] = campos_pedido + campos_produto
        context['nome_modelo_lista'] = 'pedidos'
        return context

