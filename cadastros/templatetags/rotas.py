# rotas.py
from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag
def rota_objeto(acao, objeto):
    
    nome_modelo = objeto.__class__.__name__.lower()
    nome_rota = f"{acao}-{nome_modelo}"
    return reverse(nome_rota, args=[objeto.pk])
