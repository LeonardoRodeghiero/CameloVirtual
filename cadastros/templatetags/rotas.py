# rotas.py
from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag
def rota_objeto(acao, objeto):
    
    nome_modelo = objeto.__class__.__name__.lower()
    nome_rota = f"{acao}-{nome_modelo}"
    return reverse(nome_rota, args=[objeto.pk])

@register.simple_tag
def rota_objeto_listas(nome_modelo):
    
    nome_rota = f"listar-{nome_modelo}"
    return reverse(nome_rota)


@register.simple_tag
def rota_objeto_listas_camelo(nome_modelo, camelo_id):
    nome_rota = f"listar-{nome_modelo}-camelo"
    return reverse(nome_rota, kwargs={'pk': camelo_id})

