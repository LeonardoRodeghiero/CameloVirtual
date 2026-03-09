from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Produto, Avaliacao


@receiver([post_save, post_delete], sender=Avaliacao)
def atualizar_media(sender, instance, **kwargs):
    produto = instance.produto
    if produto:
        media = Avaliacao.objects.filter(produto=produto).aggregate(Avg('nota'))['nota__avg'] or 0
        produto.avaliacao_geral = round(media, 1)
        produto.save(update_fields=['avaliacao_geral'])
        print('avaliação geral: ', media)