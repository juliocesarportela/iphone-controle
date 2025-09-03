from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, Submit, HTML
from crispy_forms.bootstrap import FormActions
from decimal import Decimal

from .models import User, Importacao, ConfiguracaoPadrao, HistoricoPreco

class ImportacaoForm(forms.ModelForm):
    """Formulário para importações com cálculos automáticos"""
    
    class Meta:
        model = Importacao
        fields = [
            'modelo', 'capacidade_gb', 'grade', 'quantidade',
            'valor_eua_unitario', 'taxa_adm_percentual', 'taxa_adm_fixa',
            'frete_eua', 'pol_eua', 'cambio_usdt', 'frete_py_usd_kg', 
            'kg_py_usd', 'status', 'preco_venda_unitario', 'data_venda'
        ]
        widgets = {
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 14 PRO MAX, 15 PRO, 11'
            }),
            'capacidade_gb': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '128, 256, 512...'
            }),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'valor_eua_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'taxa_adm_percentual': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': '0.5 para 0.5%'
            }),
            'taxa_adm_fixa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '1.90'
            }),
            'frete_eua': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '1.93'
            }),
            'pol_eua': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '10.00'
            }),
            'cambio_usdt': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '5.56 USD'
            }),
            'frete_py_usd_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '7.50'
            }),
            'kg_py_usd': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'preco_venda_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Preço de venda (BRL)'
            }),
            'data_venda': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Preenche valores padrão se existir configuração
        if self.user:
            try:
                config = ConfiguracaoPadrao.objects.get(user=self.user)
                if not self.instance.pk:  # Apenas para novos registros
                    self.fields['cambio_usdt'].initial = config.cambio_usdt_padrao
                    self.fields['frete_py_usd_kg'].initial = config.frete_py_padrao
                    self.fields['taxa_adm_fixa'].initial = config.taxa_adm_padrao
                    self.fields['frete_eua'].initial = config.frete_eua_padrao
                    self.fields['pol_eua'].initial = config.pol_eua_padrao
            except ConfiguracaoPadrao.DoesNotExist:
                pass
        

        
        # Crispy Forms Helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        
        # Adiciona atributos HTMX para cálculos em tempo real
        htmx_fields = [
            'valor_eua_unitario', 'taxa_adm_percentual', 'taxa_adm_fixa',
            'frete_eua', 'pol_eua', 'cambio_usdt', 'frete_py_usd_kg', 
            'kg_py_usd', 'quantidade'
        ]
        
        for field_name in htmx_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'hx-post': '/htmx/calcular-custos/',
                    'hx-trigger': 'input delay:500ms',
                    'hx-target': '#custos-calculados',
                    'hx-include': 'form'
                })
    
    def get_initial_for_field(self, field, field_name):
        """Sobrescrever para formatar valores iniciais sem zeros extras"""
        initial = super().get_initial_for_field(field, field_name)
        
        # Formatar taxa administrativa percentual
        if field_name == 'taxa_adm_percentual':
            # Se não há valor inicial, usar o valor padrão do modelo
            if initial is None:
                # Pegar o valor padrão do campo do modelo
                field_obj = self._meta.model._meta.get_field('taxa_adm_percentual')
                if hasattr(field_obj, 'default') and field_obj.default is not None:
                    initial = field_obj.default
            
            if initial is not None:
                try:
                    taxa_float = float(initial)
                    # Converter 0.005 para 0.5 (multiplica por 100 para exibir como porcentagem)
                    if taxa_float == 0.005:  # Valor padrão comum
                        return "0.5"
                    # Para outros valores, remover zeros desnecessários
                    elif taxa_float == int(taxa_float):
                        return f"{int(taxa_float)}"
                    else:
                        return f"{taxa_float:g}"
                except (ValueError, TypeError):
                    pass
        
        # Formatar câmbio USDT
        elif field_name == 'cambio_usdt' and initial is not None:
            try:
                cambio_float = float(initial)
                # Remover zeros desnecessários
                if cambio_float == int(cambio_float):
                    return f"{int(cambio_float)}"
                else:
                    # Formatar com até 2 casas decimais, removendo zeros à direita
                    return f"{cambio_float:.2f}".rstrip('0').rstrip('.')
            except (ValueError, TypeError):
                pass
        
        return initial

class ConfiguracaoForm(forms.ModelForm):
    """Formulário para configurações padrão do usuário"""
    
    class Meta:
        model = ConfiguracaoPadrao
        fields = [
            'cambio_usdt_padrao', 'frete_py_padrao', 'taxa_adm_padrao',
            'frete_eua_padrao', 'pol_eua_padrao'
        ]
        widgets = {
            'cambio_usdt_padrao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '5.56 USD'
            }),
            'frete_py_padrao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '7.50'
            }),
            'taxa_adm_padrao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '1.90'
            }),
            'frete_eua_padrao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '1.93'
            }),
            'pol_eua_padrao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '10.00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-4'
        self.helper.field_class = 'col-lg-8'
    
    def get_initial_for_field(self, field, field_name):
        """Sobrescrever para formatar valores iniciais sem zeros extras"""
        initial = super().get_initial_for_field(field, field_name)
        
        # Formatar câmbio USDT padrão
        if field_name == 'cambio_usdt_padrao' and initial is not None:
            try:
                cambio_float = float(initial)
                # Remover zeros desnecessários
                if cambio_float == int(cambio_float):
                    return f"{int(cambio_float)}"
                else:
                    # Formatar com até 2 casas decimais, removendo zeros à direita
                    return f"{cambio_float:.2f}".rstrip('0').rstrip('.')
            except (ValueError, TypeError):
                pass
        
        return initial

class UserForm(forms.ModelForm):
    """Formulário para edição de usuários"""
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuário'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome'
            }),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': 'Nome de Usuário',
            'email': 'E-mail',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'role': 'Função',
            'is_active': 'Usuário Ativo',
        }

class CustomUserCreationForm(UserCreationForm):
    """Formulário customizado para criação de usuários"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@exemplo.com'
        })
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sobrenome'
        })
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial='user',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuário'
            }),
        }
        labels = {
            'username': 'Nome de Usuário',
            'email': 'E-mail',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'role': 'Função',
            'password1': 'Senha',
            'password2': 'Confirmar Senha',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Digite uma senha segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user

class HistoricoPrecoForm(forms.ModelForm):
    """Formulário para histórico de preços"""
    
    class Meta:
        model = HistoricoPreco
        fields = ['modelo', 'capacidade_gb', 'grade', 'preco_eua', 'preco_venda_brl']
        widgets = {
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidade_gb': forms.NumberInput(attrs={'class': 'form-control'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'preco_eua': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'preco_venda_brl': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
        }
