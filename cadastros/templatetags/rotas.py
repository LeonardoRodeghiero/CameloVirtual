# rotas.py
from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag
def rota_objeto(acao, objeto):
    
    nome_modelo = objeto.__class__.__name__.lower()
    nome_rota = f"{acao}-{nome_modelo}"

    # Verificação: se o objeto for o vínculo, precisamos de dois IDs
    if hasattr(objeto, 'camelo_id'):
        # Passa o ID do camelo e o ID do usuário (pk)
        return reverse(nome_rota, args=[objeto.camelo_id, objeto.pk])

    return reverse(nome_rota, args=[objeto.pk])

@register.simple_tag
def rota_objeto_listas(nome_modelo):
    
    nome_rota = f"listar-{nome_modelo}"
    return reverse(nome_rota)


@register.simple_tag
def rota_objeto_listas_camelo(nome_modelo, camelo_id):
    nome_rota = f"listar-{nome_modelo}-camelo"

    # 1. Tentativa com 'camelo_id' (para a sua rota de Pedidos)
    try:
        return reverse(nome_rota, kwargs={'camelo_id': camelo_id})
    except NoReverseMatch:
        # 2. Fallback para 'pk' (para as rotas que já funcionavam antes)
        try:
            return reverse(nome_rota, kwargs={'pk': camelo_id})
        except NoReverseMatch:
            # 3. Se nada funcionar, o erro original aparece para te ajudar a depurar
            raise NoReverseMatch(f"A rota '{nome_rota}' não aceita 'camelo_id' nem 'pk'. Verifique o urls.py.")
