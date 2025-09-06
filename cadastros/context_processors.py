
from .models import Categoria

def categorias_disponiveis(request):
    return {
        'categorias_navbar': Categoria.objects.all()
    }
