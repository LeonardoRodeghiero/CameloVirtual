from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group, User
from django.urls import reverse_lazy
from .forms import UsuarioForm, PerfilForm
from django.shortcuts import get_object_or_404

from .models import Perfil
# Create your views here.

class UsuarioCreate(CreateView):
    template_name = 'cadastros/form.html'
    form_class = UsuarioForm
    success_url = reverse_lazy('login')

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