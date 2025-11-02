from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group, User
from django.urls import reverse_lazy
from .forms import UsuarioForm, PerfilForm
from django.shortcuts import get_object_or_404

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import EmailLoginForm


from .models import Perfil
# Create your views here.

class UsuarioCreate(CreateView):
    template_name = 'cadastros/form.html'
    form_class = UsuarioForm
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['titulo_form'] = "Crie Sua Conta"
        context['titulo_botao'] = "Criar"

        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = form.cleaned_data['nome_completo']  # ou gerar com base no nome
        user.email = form.cleaned_data['email']
        user.save()


        
        grupo = get_object_or_404(Group, name='cliente')
        user.groups.add(grupo)
        url = super().form_valid(form)

        # self.object.groups.add(grupo)
        # self.object.save()

        Perfil.objects.create(
            usuario=user,
            nome_completo=form.cleaned_data['nome_completo'],
            cpf=form.cleaned_data['cpf'],
            telefone=form.cleaned_data['telefone'],
            estado=form.cleaned_data['estado'],
            cidade=form.cleaned_data['cidade'],
        )
        

        return url


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

class PerfilDelete(DeleteView):
    model = Perfil
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
