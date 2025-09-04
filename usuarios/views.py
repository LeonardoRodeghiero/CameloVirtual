from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.models import Group, User
from django.urls import reverse_lazy
from .forms import UsuarioForm
from django.shortcuts import get_object_or_404

from .models import Perfil
# Create your views here.

class UsuarioCreate(CreateView):
    template_name = 'cadastros/form.html'
    form_class = UsuarioForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.username = form.cleaned_data['nome_completo']  # ou gerar com base no nome
        user.save()


        
        grupo = get_object_or_404(Group, name='cliente')

        url = super().form_valid(form)

        self.object.groups.add(grupo)
        self.object.save()

        Perfil.objects.create(
            usuario=user,
            nome_completo=form.cleaned_data['nome_completo'],
            cpf=form.cleaned_data['cpf'],
            telefone=form.cleaned_data['telefone'],
            cidade=form.cleaned_data['cidade']
        )
        

        return url


class PerfilUpdate(UpdateView):
    template_name = 'cadastros/form.html'
    model = Perfil
    fields = ['nome_completo', 'cpf', 'telefone']
    success_url = reverse_lazy('index')