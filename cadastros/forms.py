from django import forms
from .models import Avaliacao, Camelo, Produto, Categoria, Pedido
from django.core.exceptions import ValidationError


class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'mensagem']

    nota = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect
    )

class CameloIdentificacaoForm(forms.ModelForm):
    @staticmethod
    def validar_cnpj(value):
        if len(value) != 18:
            raise ValidationError("CNPJ deve ter 18 dígitos.")

        cnpj = ''.join(filter(str.isdigit, value))

        pesos1 = [5,4,3,2,9,8,7,6,5,4,3,2]
        pesos2 = [6] + pesos1

        def calcular_digito(cnpj, pesos):
            soma = sum(int(digito) * peso for digito, peso in zip(cnpj, pesos))
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)

        digito1 = calcular_digito(cnpj[:12], pesos1)
        digito2 = calcular_digito(cnpj[:12] + digito1, pesos2)

        if cnpj[-2:] != digito1 + digito2:
            raise ValidationError("CNPJ inválido.")

    def clean_cnpj(self):
        value = self.cleaned_data['cnpj']
        # chama sua função validar_cnpj
        try:
            self.validar_cnpj(value)
        except ValidationError as e:
            raise e
        return value

    class Meta:
        model = Camelo
        fields = ["nome_fantasia", "cnpj"]

class CameloContatoForm(forms.ModelForm):
    class Meta:
        model = Camelo
        fields = ["email", "telefone"]

class CameloPerfilForm(forms.ModelForm):
    class Meta:
        model = Camelo
        fields = ["descricao_loja", "imagem_logo"]

class CameloEnderecoForm(forms.ModelForm):
    class Meta:
        model = Camelo
        fields = ["estado", "cidade", "bairro", "logradouro", "numero", "complemento", "cep"]





class ProdutoInformacaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.camelo_id = kwargs.pop('camelo_id', None)
        super().__init__(*args, **kwargs)
        if self.camelo_id:
            self.fields['categoria'].queryset = Categoria.objects.filter(camelo_id=self.camelo_id)

    class Meta:
        model = Produto
        fields = ["nome", "marca", "categoria"]


    

class ProdutoDetalhesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.camelo_id = kwargs.pop('camelo_id', None)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Produto
        fields = ["descricao", "preco", "quantidade"]

class ProdutoImagemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.camelo_id = kwargs.pop('camelo_id', None)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Produto
        fields = ["imagem"]

class ProdutoFornecedorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.camelo_id = kwargs.pop('camelo_id', None)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Produto
        fields = ["fornecedor"]




class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["opcao_pedido"]
        widgets = {
            "opcao_pedido": forms.RadioSelect
        }
