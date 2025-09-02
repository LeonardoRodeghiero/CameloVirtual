from django.db import models

from django.contrib.auth.models import User
# Create your models here.

class Categoria(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.CharField(max_length=80)

    def __str__(self):
        return f"{self.nome}"

