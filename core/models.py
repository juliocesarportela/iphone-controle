from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class User(AbstractUser):
    """Modelo de usuário personalizado"""
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('user', 'Usuário'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username

class ConfiguracaoPadrao(models.Model):
    """Configurações padrão por usuário"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cambio_usdt_padrao = models.DecimalField(
        max_digits=10, decimal_places=4, 
        default=Decimal('5.56'),
        help_text="Taxa de câmbio USDT padrão"
    )
    frete_py_padrao = models.DecimalField(
        max_digits=10, decimal_places=2, 
        default=Decimal('7.50'),
        help_text="Frete Paraguay padrão por kg (USD)"
    )
    taxa_adm_padrao = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('1.90'),
        help_text="Taxa administrativa padrão (USD)"
    )
    frete_eua_padrao = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('1.93'),
        help_text="Frete EUA padrão (USD)"
    )
    pol_eua_padrao = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('10.00'),
        help_text="POL EUA padrão (USD)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuração Padrão'
        verbose_name_plural = 'Configurações Padrão'
    
    def __str__(self):
        return f"Configurações de {self.user.username}"

class Importacao(models.Model):
    """Modelo principal de importação baseado na planilha Excel"""
    STATUS_CHOICES = [
        ('planejado', 'Planejado'),
        ('em_transito', 'Em Trânsito'),
        ('recebido', 'Recebido'),
        ('vendido', 'Vendido'),
    ]
    
    GRADE_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('C', 'C'),
    ]
    
    # Campos básicos do produto
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    modelo = models.CharField(
        max_length=50,
        help_text="Modelo do iPhone (ex: 11, 14 PRO MAX, 15 PRO)"
    )
    capacidade_gb = models.IntegerField(
        validators=[MinValueValidator(64)],
        help_text="Capacidade em GB (128, 256, 512, etc.)"
    )
    grade = models.CharField(
        max_length=2, 
        choices=GRADE_CHOICES,
        help_text="Grade do produto"
    )
    quantidade = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantidade de unidades"
    )
    
    # Custos EUA (baseados na planilha)
    valor_eua_unitario = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Valor unitário nos EUA (USD)"
    )
    taxa_adm_percentual = models.DecimalField(
        max_digits=5, decimal_places=3, 
        default=Decimal('0.005'),  # 0.5%
        help_text="Taxa administrativa percentual (0.005 = 0.5%)"
    )
    taxa_adm_fixa = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('1.90'),
        help_text="Taxa administrativa fixa (USD)"
    )
    frete_eua = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('1.93'),
        help_text="Frete nos EUA (USD)"
    )
    pol_eua = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('10.00'),
        help_text="POL nos EUA (USD)"
    )
    
    # Conversão e Frete PY
    cambio_usdt = models.DecimalField(
        max_digits=10, decimal_places=4,
        default=Decimal('5.56'),
        help_text="Taxa de câmbio USDT"
    )
    frete_py_usd_kg = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('7.50'),
        help_text="Frete PY (USD/kg)"
    )
    kg_py_usd = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('0.00'),
        help_text="KG PY ($)"
    )
    
    # Datas e Status
    data_importacao = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='planejado'
    )
    
    # Venda (opcional)
    preco_venda_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, 
        null=True, blank=True,
        help_text="Preço de venda unitário (BRL)"
    )
    data_venda = models.DateField(
        null=True, blank=True,
        help_text="Data da venda"
    )
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Importação'
        verbose_name_plural = 'Importações'
    
    # Métodos para cálculos (properties) - lógica ajustada conforme especificações
    @property
    def custo_eua_base(self):
        """Custo base nos EUA (valor + taxa ADM + frete + polimento)"""
        return self.valor_eua_unitario + self.taxa_adm_fixa + self.frete_eua + self.pol_eua
    
    @property
    def custo_eua_total(self):
        """Custo EUA + 0,5% (taxa variável por importação)"""
        return self.custo_eua_base * (1 + self.taxa_adm_percentual)
    
    @property
    def custo_eua_brl(self):
        """Custo EUA convertido para BRL"""
        return self.custo_eua_total * self.cambio_usdt
    
    @property
    def frete_py_usd(self):
        """Frete PY ($) = Frete PY (USD/kg) + KG PY ($)"""
        return self.frete_py_usd_kg + self.kg_py_usd
    
    @property
    def frete_py_brl(self):
        """Frete PY convertido para BRL"""
        return self.frete_py_usd * self.cambio_usdt
    
    @property
    def custo_total_py_usd(self):
        """Custo PY = Custo EUA + Frete PY (ambos em USD)"""
        return self.custo_eua_total + self.frete_py_usd
    
    @property
    def custo_total_py_brl(self):
        """Custo PY convertido para BRL usando câmbio USDT"""
        return self.custo_total_py_usd * self.cambio_usdt
    
    @property
    def custo_total_quantidade_usd(self):
        """Custo total para toda a quantidade em USD"""
        return self.custo_total_py_usd * self.quantidade
    
    @property
    def custo_total_quantidade_brl(self):
        """Custo total para toda a quantidade em BRL"""
        return self.custo_total_py_brl * self.quantidade
    
    @property
    def lucro_unitario(self):
        """Lucro por unidade (se vendido)"""
        if self.preco_venda_unitario:
            return self.preco_venda_unitario - self.custo_total_py_brl
        return None
    
    @property
    def lucro_total(self):
        """Lucro total (se vendido)"""
        lucro_unit = self.lucro_unitario
        if lucro_unit is not None:
            return lucro_unit * self.quantidade
        return None
    
    @property
    def margem_percentual(self):
        """Margem de lucro percentual"""
        lucro = self.lucro_unitario
        if lucro is not None and self.custo_total_py_brl > 0:
            return (lucro / self.custo_total_py_brl) * 100
        return None
    
    def __str__(self):
        return f"iPhone {self.modelo} {self.capacidade_gb}GB - {self.grade} (x{self.quantidade})"

class HistoricoPreco(models.Model):
    """Histórico de preços para análise de tendências"""
    modelo = models.CharField(max_length=50)
    capacidade_gb = models.IntegerField()
    grade = models.CharField(max_length=2)
    preco_eua = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda_brl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_registro = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-data_registro']
        verbose_name = 'Histórico de Preço'
        verbose_name_plural = 'Histórico de Preços'
    
    def __str__(self):
        return f"{self.modelo} {self.capacidade_gb}GB {self.grade} - ${self.preco_eua}"
