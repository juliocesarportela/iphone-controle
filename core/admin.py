from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Importacao, ConfiguracaoPadrao, HistoricoPreco

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personalizado para usuários"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('role',)}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('role',)}),
    )

@admin.register(ConfiguracaoPadrao)
class ConfiguracaoPadraoAdmin(admin.ModelAdmin):
    """Admin para configurações padrão"""
    list_display = ('user', 'cambio_usdt_padrao', 'frete_py_padrao', 'taxa_adm_padrao', 'updated_at')
    list_filter = ('updated_at', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Configurações de Câmbio', {
            'fields': ('cambio_usdt_padrao',)
        }),
        ('Configurações de Taxas', {
            'fields': ('taxa_adm_padrao', 'frete_eua_padrao', 'pol_eua_padrao')
        }),
        ('Configurações de Frete', {
            'fields': ('frete_py_padrao',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Importacao)
class ImportacaoAdmin(admin.ModelAdmin):
    """Admin para importações"""
    list_display = (
        'modelo_display', 'capacidade_gb', 'grade', 'quantidade', 
        'status_display', 'custo_total_brl_display', 'lucro_display', 
        'user', 'data_importacao'
    )
    list_filter = (
        'status', 'grade', 'modelo', 'capacidade_gb', 
        'data_importacao', 'user'
    )
    search_fields = ('modelo', 'user__username')
    readonly_fields = (
        'custo_eua_total', 'custo_eua_brl', 'frete_py_usd', 'frete_py_brl',
        'custo_total_py_usd', 'custo_total_py_brl', 'custo_total_quantidade_usd',
        'custo_total_quantidade_brl', 'lucro_unitario', 'lucro_total', 
        'margem_percentual', 'created_at', 'updated_at'
    )
    ordering = ('-created_at',)
    date_hierarchy = 'data_importacao'
    
    fieldsets = (
        ('Produto', {
            'fields': ('user', 'modelo', 'capacidade_gb', 'grade', 'quantidade', 'peso_kg')
        }),
        ('Custos EUA', {
            'fields': (
                'valor_eua_unitario', 'taxa_adm_fixa', 'taxa_adm_percentual',
                'frete_eua', 'pol_eua'
            )
        }),
        ('Conversão e Frete PY', {
            'fields': ('cambio_usdt', 'frete_py_por_kg')
        }),
        ('Status e Datas', {
            'fields': ('status', 'data_importacao')
        }),
        ('Venda (Opcional)', {
            'fields': ('preco_venda_unitario', 'data_venda'),
            'classes': ('collapse',)
        }),
        ('Cálculos Automáticos', {
            'fields': (
                'custo_eua_total', 'custo_eua_brl', 'frete_py_usd', 'frete_py_brl',
                'custo_total_py_usd', 'custo_total_py_brl', 'custo_total_quantidade_usd',
                'custo_total_quantidade_brl', 'lucro_unitario', 'lucro_total', 
                'margem_percentual'
            ),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def modelo_display(self, obj):
        return format_html(
            '<strong>iPhone {}</strong>',
            obj.modelo
        )
    modelo_display.short_description = 'Modelo'
    
    def status_display(self, obj):
        colors = {
            'planejado': '#6B7280',
            'em_transito': '#3B82F6',
            'recebido': '#F59E0B',
            'vendido': '#10B981'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6B7280'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def custo_total_brl_display(self, obj):
        return format_html(
            'R$ <strong>{:,.2f}</strong>',
            obj.custo_total_quantidade_brl
        )
    custo_total_brl_display.short_description = 'Custo Total (BRL)'
    
    def lucro_display(self, obj):
        if obj.lucro_total is not None:
            color = '#10B981' if obj.lucro_total >= 0 else '#EF4444'
            return format_html(
                '<span style="color: {}; font-weight: bold;">R$ {:,.2f}</span>',
                color,
                obj.lucro_total
            )
        return '-'
    lucro_display.short_description = 'Lucro Total'

@admin.register(HistoricoPreco)
class HistoricoPrecoAdmin(admin.ModelAdmin):
    """Admin para histórico de preços"""
    list_display = ('modelo', 'capacidade_gb', 'grade', 'preco_eua', 'preco_venda_brl', 'data_registro', 'user')
    list_filter = ('modelo', 'capacidade_gb', 'grade', 'data_registro', 'user')
    search_fields = ('modelo', 'user__username')
    ordering = ('-data_registro',)
    date_hierarchy = 'data_registro'
    
    fieldsets = (
        ('Produto', {
            'fields': ('user', 'modelo', 'capacidade_gb', 'grade')
        }),
        ('Preços', {
            'fields': ('preco_eua', 'preco_venda_brl')
        }),
        ('Data', {
            'fields': ('data_registro',)
        })
    )

# Customização do Admin Site
admin.site.site_header = 'iPhone Import Manager'
admin.site.site_title = 'iPhone Import Admin'
admin.site.index_title = 'Administração do Sistema'
