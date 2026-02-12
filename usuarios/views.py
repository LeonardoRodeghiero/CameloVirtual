from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group, User
from django.urls import reverse_lazy
from .forms import UsuarioForm, PerfilForm
from django.shortcuts import get_object_or_404

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import EmailLoginForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login

from .models import Perfil, CadastroPendente
from django import forms

from django.contrib import messages
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

# Create your views here.

class UsuarioCreate(CreateView):
    template_name = 'cadastros/form.html'
    form_class = UsuarioForm
    success_url = reverse_lazy('confirmar-codigo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo_form'] = "Crie Sua Conta"
        context['titulo_botao'] = "Criar"

        return context
    
    


    # def form_valid(self, form):
    #     user = form.save(commit=False)
    #     user.username = form.cleaned_data['nome_completo']
    #     user.email = form.cleaned_data['email']
    #     user.save()

    #     grupo = get_object_or_404(Group, name='cliente')
    #     user.groups.add(grupo)

    #     Perfil.objects.create(
    #         usuario=user,
    #         nome_completo=form.cleaned_data['nome_completo'],
    #         cpf=form.cleaned_data['cpf'],
    #         telefone=form.cleaned_data['telefone'],
    #         estado=form.cleaned_data['estado'],
    #         cidade=form.cleaned_data['cidade'],
    #     )

    #     login(self.request, user)

    #     self.object = user

    #     return redirect(self.success_url)

    def form_valid(self, form):
        dados = form.cleaned_data

        cadastro = CadastroPendente.objects.create(
            nome_completo=dados['nome_completo'],
            email=dados['email'], # vai virar o email do User
            senha=make_password(dados['password1']), # senha em texto puro, hash será aplicado depois
            cpf=dados['cpf'],
            telefone=dados['telefone'],
            estado=dados['estado'],
            cidade=dados['cidade'],
            bairro=dados.get('bairro'),
            logradouro=dados.get('logradouro'),
            numero=dados.get('numero'),
            complemento=dados.get('complemento'),
            cep=dados.get('cep'),
        )
        cadastro.gerar_codigo()

        send_mail(
            "Confirmação de cadastro",
            f"Seu código é {cadastro.codigo}",
            "rodeghieroleonardo@gmail.com", # AQUI É O EMAIL QUE ENVIA OS CÓDIGOS
            [cadastro.email]
        )

        return redirect("confirmar-codigo", email=cadastro.email)



def confirmar_codigo(request, email):
    cadastro = get_object_or_404(CadastroPendente, email=email)

    if cadastro.expirado(): 
        cadastro.delete() 
        return render(request, "paginas/confirmar.html", { 
            "expirou": "Este cadastro expirou. Faça o registro novamente.", 
            "email": email 
        })

    if request.method == "POST":
        codigo = request.POST.get("codigo")

        if codigo == cadastro.codigo:
            # cria usuário real
            user = User.objects.create(
                username=cadastro.nome_completo,
                email=cadastro.email,
                password=cadastro.senha  # já está com hash
            )

            grupo = Group.objects.get(name="cliente")
            user.groups.add(grupo)

            Perfil.objects.create(
                usuario=user,
                nome_completo=cadastro.nome_completo,
                cpf=cadastro.cpf,
                telefone=cadastro.telefone,
                estado=cadastro.estado,
                cidade=cadastro.cidade,
                bairro=cadastro.bairro,
                logradouro=cadastro.logradouro,
                numero=cadastro.numero,
                complemento=cadastro.complemento,
                cep=cadastro.cep,
            )

            cadastro.delete()
            login(request, user)
            return redirect("index")

        return render(request, "paginas/confirmar.html", {"erro": "Código inválido", "email": email})

    return render(request, "paginas/confirmar.html", {"email": email})





class PerfilUpdate(UpdateView):
    template_name = 'cadastros/form.html'
    form_class = PerfilForm
    model = Perfil
    success_url = reverse_lazy('index')

    def get_form_kwargs(self):  
        kwargs = super().get_form_kwargs()
        kwargs['usuario_logado'] = self.request.user       
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo_form'] = "Informações do Perfil"
        context['titulo_botao'] = "Atualizar"

        return context





    def form_valid(self, form):
        perfil = form.save(commit=False)
        
        # Atualiza os dados do usuário
        user = perfil.usuario  # supondo que Perfil tem um campo OneToOne com User
        user.username = form.cleaned_data['nome_completo']
        user.email = form.cleaned_data['email']
        user.save()

        user.groups.clear()

        if perfil.tipo == 'administrador':
            grupo = Group.objects.get(name='administrador')
        else:
            grupo = Group.objects.get(name='cliente')

        user.groups.add(grupo)

        perfil.save()
        return super().form_valid(form)

class UsuarioDelete(LoginRequiredMixin, DeleteView):
    model = User
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('index')



def login_email_view(request):
    form = EmailLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # ou outra página
            else:
                form.add_error(None, 'Email ou senha inválidos.')
        except User.DoesNotExist:
            form.add_error('email', 'Email não encontrado.')

    return render(request, 'cadastros/form.html', {
        'form': form,
        'titulo_form': 'Entre Na Sua Conta',
        'titulo_botao': "Entrar",

    })
