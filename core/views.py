from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Avg, Count, Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from decimal import Decimal

# PDF and Excel export imports (conditional)
REPORTLAB_AVAILABLE = False
XLSXWRITER_AVAILABLE = False
MATPLOTLIB_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    pass

try:
    import xlsxwriter
    XLSXWRITER_AVAILABLE = True
except ImportError:
    pass

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    pass

import json
from datetime import datetime, timedelta
import io
import base64

from .models import User, Importacao, ConfiguracaoPadrao, HistoricoPreco
from .forms import ImportacaoForm, ConfiguracaoForm, UserForm

@login_required
def dashboard(request):
    """Dashboard principal com métricas e gráficos"""
    user = request.user
    
    # Buscar todas as importações do usuário
    importacoes = Importacao.objects.filter(user=user)
    
    # Estatísticas gerais (calculadas manualmente)
    total_importacoes = importacoes.count()
    total_investido_usd = sum([imp.custo_total_quantidade_usd for imp in importacoes])
    total_investido_brl = sum([imp.custo_total_quantidade_brl for imp in importacoes])
    
    # Importações por status (calculadas manualmente)
    status_stats = {}
    for status_choice in Importacao.STATUS_CHOICES:
        status_key = status_choice[0]
        status_importacoes = importacoes.filter(status=status_key)
        if status_importacoes.exists():
            status_stats[status_key] = {
                'count': status_importacoes.count(),
                'valor_total': sum([imp.custo_total_quantidade_brl for imp in status_importacoes]),
                'display': status_choice[1]
            }
    
    # Importações recentes
    importacoes_recentes = importacoes.order_by('-created_at')[:5]
    
    # Modelos mais importados (usando agregação em campos reais)
    modelos_populares = importacoes.values('modelo').annotate(
        count=Count('id'),
        total_unidades=Sum('quantidade')
    ).order_by('-count')[:5]
    
    # Lucro total (apenas vendidos)
    vendidos = importacoes.filter(status='vendido')
    lucro_total = sum([imp.lucro_total for imp in vendidos if imp.lucro_total])
    
    context = {
        'total_importacoes': total_importacoes,
        'total_investido_usd': total_investido_usd,
        'total_investido_brl': total_investido_brl,
        'status_stats': status_stats,
        'importacoes_recentes': importacoes_recentes,
        'modelos_populares': modelos_populares,
        'lucro_total': lucro_total,
    }
    
    return render(request, 'dashboard/index.html', context)

@login_required
def importacao_list(request):
    """Lista todas as importações do usuário"""
    importacoes = Importacao.objects.filter(user=request.user)
    
    # Filtros
    modelo = request.GET.get('modelo')
    status = request.GET.get('status')
    grade = request.GET.get('grade')
    
    if modelo:
        importacoes = importacoes.filter(modelo__icontains=modelo)
    if status:
        importacoes = importacoes.filter(status=status)
    if grade:
        importacoes = importacoes.filter(grade=grade)
    
    # Paginação
    paginator = Paginator(importacoes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opções para filtros
    modelos_disponiveis = Importacao.objects.filter(user=request.user).values_list('modelo', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'modelos_disponiveis': modelos_disponiveis,
        'status_choices': Importacao.STATUS_CHOICES,
        'grade_choices': Importacao.GRADE_CHOICES,
        'filtros': {
            'modelo': modelo,
            'status': status,
            'grade': grade,
        }
    }
    
    return render(request, 'importacoes/list.html', context)

@login_required
def importacao_create(request):
    """Criar nova importação"""
    if request.method == 'POST':
        form = ImportacaoForm(request.POST, user=request.user)
        if form.is_valid():
            importacao = form.save(commit=False)
            importacao.user = request.user
            importacao.save()
            
            messages.success(request, 'Importação criada com sucesso!')
            return redirect('core:importacao_detail', pk=importacao.pk)
    else:
        form = ImportacaoForm(user=request.user)
    
    return render(request, 'importacoes/form.html', {
        'form': form,
        'title': 'Nova Importação'
    })

@login_required
def importacao_detail(request, pk):
    """Detalhes de uma importação"""
    importacao = get_object_or_404(Importacao, pk=pk, user=request.user)
    
    context = {
        'importacao': importacao,
    }
    
    return render(request, 'importacoes/detail.html', context)

@login_required
def importacao_update(request, pk):
    """Editar importação"""
    importacao = get_object_or_404(Importacao, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ImportacaoForm(request.POST, instance=importacao, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Importação atualizada com sucesso!')
            return redirect('core:importacao_detail', pk=importacao.pk)
    else:
        form = ImportacaoForm(instance=importacao, user=request.user)
    
    return render(request, 'importacoes/form.html', {
        'form': form,
        'object': importacao,
        'title': 'Editar Importação'
    })

@login_required
def importacao_delete(request, pk):
    """Deletar importação"""
    importacao = get_object_or_404(Importacao, pk=pk, user=request.user)
    
    if request.method == 'POST':
        importacao.delete()
        messages.success(request, 'Importação deletada com sucesso!')
        return redirect('core:importacao_list')
    
    return render(request, 'importacoes/delete.html', {
        'importacao': importacao
    })

@login_required
@require_http_methods(["POST"])
def calcular_custos_htmx(request):
    """Endpoint HTMX para cálculos em tempo real"""
    try:
        # DEBUG TEMPORÁRIO - Valores do usuário
        print("\n=== DEBUG CÁLCULOS HTMX ===")
        print(f"POST data completo: {dict(request.POST)}")
        
        # Extrai dados do formulário com valores padrão mais robustos
        valor_eua_str = request.POST.get('valor_eua_unitario', '0')
        try:
            valor_eua = Decimal(str(valor_eua_str).replace(',', '.')) if valor_eua_str and valor_eua_str != '' else Decimal('0')
        except (ValueError, TypeError):
            valor_eua = Decimal('0')
        print(f"Valor EUA String: '{valor_eua_str}' -> Decimal: {valor_eua}")
        
        taxa_adm_fixa_str = request.POST.get('taxa_adm_fixa', '1.90')
        try:
            taxa_adm_fixa = Decimal(str(taxa_adm_fixa_str).replace(',', '.')) if taxa_adm_fixa_str and taxa_adm_fixa_str != '' else Decimal('1.90')
        except (ValueError, TypeError):
            taxa_adm_fixa = Decimal('1.90')
        
        taxa_adm_perc_str = request.POST.get('taxa_adm_percentual', '0.005')
        try:
            taxa_adm_perc_raw = Decimal(str(taxa_adm_perc_str).replace(',', '.')) if taxa_adm_perc_str and taxa_adm_perc_str != '' else Decimal('0.005')
        except (ValueError, TypeError):
            taxa_adm_perc_raw = Decimal('0.005')
        
        # Se o valor for maior que 1, assume que foi digitado como porcentagem (ex: 0.5 para 0.5%)
        # Se for menor que 1, assume que já está no formato decimal correto (ex: 0.005)
        if taxa_adm_perc_raw > 1:
            taxa_adm_perc = taxa_adm_perc_raw / 100  # Ex: 50 -> 0.5
        elif taxa_adm_perc_raw > 0.1:
            taxa_adm_perc = taxa_adm_perc_raw / 100  # Ex: 0.5 -> 0.005
        else:
            taxa_adm_perc = taxa_adm_perc_raw  # Ex: 0.005 -> 0.005 (já está correto)
        
        frete_eua_str = request.POST.get('frete_eua', '1.93')
        try:
            frete_eua = Decimal(str(frete_eua_str).replace(',', '.')) if frete_eua_str and frete_eua_str != '' else Decimal('1.93')
        except (ValueError, TypeError):
            frete_eua = Decimal('1.93')
        
        pol_eua_str = request.POST.get('pol_eua', '10.00')
        try:
            pol_eua = Decimal(str(pol_eua_str).replace(',', '.')) if pol_eua_str and pol_eua_str != '' else Decimal('10.00')
        except (ValueError, TypeError):
            pol_eua = Decimal('10.00')
        
        cambio_str = request.POST.get('cambio_usdt', '5.56')
        try:
            cambio = Decimal(str(cambio_str).replace(',', '.')) if cambio_str and cambio_str != '' else Decimal('5.56')
        except (ValueError, TypeError):
            cambio = Decimal('5.56')
        
        frete_py_usd_kg_str = request.POST.get('frete_py_usd_kg', '7.50')
        try:
            frete_py_usd_kg = Decimal(str(frete_py_usd_kg_str).replace(',', '.')) if frete_py_usd_kg_str and frete_py_usd_kg_str != '' else Decimal('7.50')
        except (ValueError, TypeError):
            frete_py_usd_kg = Decimal('7.50')
        
        kg_py_usd_str = request.POST.get('kg_py_usd', '0.00')
        try:
            kg_py_usd = Decimal(str(kg_py_usd_str).replace(',', '.')) if kg_py_usd_str and kg_py_usd_str != '' else Decimal('0.00')
        except (ValueError, TypeError):
            kg_py_usd = Decimal('0.00')
        
        quantidade_str = request.POST.get('quantidade', '1')
        quantidade = int(quantidade_str) if quantidade_str and quantidade_str != '' else 1
        
        # DEBUG - Todos os valores extraídos
        print(f"Taxa ADM Fixa: '{taxa_adm_fixa_str}' -> {taxa_adm_fixa}")
        print(f"Taxa ADM Perc Raw: '{taxa_adm_perc_str}' -> {taxa_adm_perc_raw}")
        print(f"Taxa ADM Perc Final: {taxa_adm_perc} (conversão aplicada)")
        print(f"Frete EUA: '{frete_eua_str}' -> {frete_eua}")
        print(f"POL EUA: '{pol_eua_str}' -> {pol_eua}")
        print(f"Câmbio: '{cambio_str}' -> {cambio}")
        print(f"Frete PY USD/kg: '{frete_py_usd_kg_str}' -> {frete_py_usd_kg}")
        print(f"KG PY USD: '{kg_py_usd_str}' -> {kg_py_usd}")
        print(f"Quantidade: '{quantidade_str}' -> {quantidade}")
        
        # Cálculos baseados na lógica EXATA da planilha
        # 1. CUSTO EUA = (VALOR EUA + TAXA ADM + FRETE EUA + POL EUA) * (1 + taxa_percentual)
        custo_eua_base = valor_eua + taxa_adm_fixa + frete_eua + pol_eua
        custo_eua_total = custo_eua_base * (1 + taxa_adm_perc)  # Taxa definida pelo usuário
        
        # 2. CUSTO BRL = CUSTO EUA * CÂMBIO USDT
        custo_eua_brl = custo_eua_total * cambio
        
        # 3. FRETE PY USD = FRETE PY (USD/kg) + KG PY ($) - SOMA, não multiplicação
        # Conforme modelo: frete_py_usd = frete_py_usd_kg + kg_py_usd
        frete_py_usd_unitario = frete_py_usd_kg + kg_py_usd
        
        # 4. FRETE PY BRL = FRETE PY USD * CÂMBIO USDT
        frete_py_brl_unitario = frete_py_usd_unitario * cambio
        
        # 5. CUSTO TOTAL PY USD = CUSTO EUA + FRETE PY USD
        custo_total_py_usd_unitario = custo_eua_total + frete_py_usd_unitario
        
        # 6. CUSTO TOTAL PY BRL = CUSTO TOTAL PY USD * CÂMBIO USDT
        custo_total_py_brl_unitario = custo_total_py_usd_unitario * cambio
        
        # Custos totais para quantidade
        custo_total_quantidade_usd = custo_total_py_usd_unitario * quantidade
        custo_total_quantidade_brl = custo_total_py_brl_unitario * quantidade
        
        # DEBUG - Cálculos intermediários e finais
        print(f"\nCÁLCULOS INTERMEDIÁRIOS:")
        print(f"Custo EUA Base: {custo_eua_base}")
        print(f"Custo EUA Total: {custo_eua_total}")
        print(f"Custo EUA BRL: {custo_eua_brl}")
        print(f"Frete PY USD Unitário: {frete_py_usd_unitario}")
        print(f"Frete PY BRL Unitário: {frete_py_brl_unitario}")
        print(f"Custo Total PY USD Unitário: {custo_total_py_usd_unitario}")
        print(f"Custo Total PY BRL Unitário: {custo_total_py_brl_unitario}")
        print(f"Custo Total Quantidade USD: {custo_total_quantidade_usd}")
        print(f"Custo Total Quantidade BRL: {custo_total_quantidade_brl}")
        print("=== FIM DEBUG ===")
        
        context = {
            'custo_eua_total': custo_eua_total,
            'custo_eua_brl': custo_eua_brl,
            'frete_py_usd': frete_py_usd_unitario,
            'frete_py_brl': frete_py_brl_unitario,
            'custo_total_py_usd': custo_total_py_usd_unitario,
            'custo_total_py_brl': custo_total_py_brl_unitario,
            'custo_total_quantidade_usd': custo_total_quantidade_usd,
            'custo_total_quantidade_brl': custo_total_quantidade_brl,
        }
        
        return render(request, 'partials/custos_calculados.html', context)
    
    except (ValueError, TypeError) as e:
        return HttpResponse('<div class="text-red-500">Erro nos cálculos. Verifique os valores.</div>')

@login_required
def relatorios(request):
    """Página principal de relatórios com múltiplos relatórios úteis"""
    user = request.user
    importacoes = Importacao.objects.filter(user=user)
    
    # 1. Relatório de Rentabilidade por Modelo
    rentabilidade_modelo = []
    modelos = importacoes.values('modelo').distinct()
    
    for modelo_dict in modelos:
        modelo = modelo_dict['modelo']
        modelo_importacoes = importacoes.filter(modelo=modelo)
        
        total_investido = sum([imp.custo_total_quantidade_brl for imp in modelo_importacoes])
        vendidos = modelo_importacoes.filter(status='vendido')
        total_vendido = sum([imp.preco_venda_unitario * imp.quantidade for imp in vendidos if imp.preco_venda_unitario])
        lucro_total = sum([imp.lucro_total for imp in vendidos if imp.lucro_total])
        
        rentabilidade_modelo.append({
            'modelo': modelo,
            'total_importacoes': modelo_importacoes.count(),
            'total_unidades': sum([imp.quantidade for imp in modelo_importacoes]),
            'total_investido': total_investido,
            'total_vendido': total_vendido,
            'lucro_total': lucro_total,
            'margem_media': (lucro_total / total_investido * 100) if total_investido > 0 else 0
        })
    
    # 2. Relatório de Status de Importações
    status_report = []
    for status_choice in Importacao.STATUS_CHOICES:
        status_key = status_choice[0]
        status_importacoes = importacoes.filter(status=status_key)
        if status_importacoes.exists():
            total_valor = sum([imp.custo_total_quantidade_brl for imp in status_importacoes])
            total_unidades = sum([imp.quantidade for imp in status_importacoes])
            status_report.append({
                'status': status_choice[1],
                'status_key': status_key,
                'count': status_importacoes.count(),
                'total_unidades': total_unidades,
                'total_valor': total_valor,
                'valor_medio': total_valor / status_importacoes.count() if status_importacoes.count() > 0 else 0
            })
    
    # 3. Relatório de Análise de Custos (EUA vs Paraguay)
    analise_custos = []
    for imp in importacoes[:10]:  # Top 10 para não sobrecarregar
        diferenca_custo = imp.custo_total_py_brl - imp.custo_eua_brl
        percentual_diferenca = (diferenca_custo / imp.custo_eua_brl * 100) if imp.custo_eua_brl > 0 else 0
        
        analise_custos.append({
            'modelo': imp.modelo,
            'capacidade': imp.capacidade_gb,
            'grade': imp.grade,
            'custo_eua': imp.custo_eua_brl,
            'custo_py': imp.custo_total_py_brl,
            'diferenca': diferenca_custo,
            'percentual_diferenca': percentual_diferenca
        })
    
    # 4. Relatório de Performance por Grade
    performance_grade = []
    grades = importacoes.values('grade').distinct()
    
    for grade_dict in grades:
        grade = grade_dict['grade']
        grade_importacoes = importacoes.filter(grade=grade)
        
        total_investido = sum([imp.custo_total_quantidade_brl for imp in grade_importacoes])
        vendidos = grade_importacoes.filter(status='vendido')
        total_vendido = sum([imp.preco_venda_unitario * imp.quantidade for imp in vendidos if imp.preco_venda_unitario])
        lucro_total = sum([imp.lucro_total for imp in vendidos if imp.lucro_total])
        
        performance_grade.append({
            'grade': grade,
            'total_importacoes': grade_importacoes.count(),
            'total_unidades': sum([imp.quantidade for imp in grade_importacoes]),
            'total_investido': total_investido,
            'total_vendido': total_vendido,
            'lucro_total': lucro_total,
            'margem_media': (lucro_total / total_investido * 100) if total_investido > 0 else 0
        })
    
    # 5. Estatísticas Gerais
    estatisticas_gerais = {
        'total_importacoes': importacoes.count(),
        'total_unidades': sum([imp.quantidade for imp in importacoes]),
        'total_investido_usd': sum([imp.custo_total_quantidade_usd for imp in importacoes]),
        'total_investido_brl': sum([imp.custo_total_quantidade_brl for imp in importacoes]),
        'valor_medio_unitario': sum([imp.custo_total_py_brl for imp in importacoes]) / importacoes.count() if importacoes.count() > 0 else 0,
        'modelos_unicos': modelos.count(),
        'grades_unicas': grades.count()
    }
    
    # 6. Importações Recentes
    importacoes_recentes = importacoes.order_by('-created_at')[:10]
    
    # 7. Totais para o resumo geral de rentabilidade
    rentabilidade_totals = {
        'total_investido': sum([item['total_investido'] for item in rentabilidade_modelo]),
        'total_vendido': sum([item['total_vendido'] for item in rentabilidade_modelo]),
        'total_lucro': sum([item['lucro_total'] for item in rentabilidade_modelo])
    }
    
    # 8. Métricas de performance para análise
    performance_metrics = {
        'modelos_lucrativos': len([item for item in rentabilidade_modelo if item['lucro_total'] > 0]),
        'modelos_prejuizo': len([item for item in rentabilidade_modelo if item['lucro_total'] < 0]),
        'melhor_modelo': max(rentabilidade_modelo, key=lambda x: x['margem_media']) if rentabilidade_modelo else None,
        'pior_modelo': min(rentabilidade_modelo, key=lambda x: x['margem_media']) if rentabilidade_modelo else None
    }
    
    context = {
        'rentabilidade_modelo': sorted(rentabilidade_modelo, key=lambda x: x['margem_media'], reverse=True),
        'rentabilidade_totals': rentabilidade_totals,
        'performance_metrics': performance_metrics,
        'status_report': status_report,
        'analise_custos': analise_custos,
        'performance_grade': sorted(performance_grade, key=lambda x: x['margem_media'], reverse=True),
        'estatisticas_gerais': estatisticas_gerais,
        'importacoes_recentes': importacoes_recentes,
    }
    
    return render(request, 'relatorios/index.html', context)

# Export Functions
def generate_chart_base64(data, chart_type='bar', title='Chart', xlabel='X', ylabel='Y'):
    """Generate a base64 encoded chart for PDF reports"""
    plt.figure(figsize=(10, 6))
    
    if chart_type == 'bar':
        plt.bar(range(len(data)), [item['value'] for item in data])
        plt.xticks(range(len(data)), [item['label'] for item in data], rotation=45)
    elif chart_type == 'pie':
        plt.pie([item['value'] for item in data], labels=[item['label'] for item in data], autopct='%1.1f%%')
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64

@login_required
def export_relatorio_pdf(request, tipo_relatorio):
    """Export reports to PDF"""
    if not EXPORT_AVAILABLE:
        messages.error(request, 'Bibliotecas de exportação não estão instaladas. Execute: pip install reportlab xlsxwriter matplotlib seaborn')
        return redirect('core:relatorios')
    
    user = request.user
    importacoes = Importacao.objects.filter(user=user)
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    if tipo_relatorio == 'rentabilidade':
        # Rentability Report
        elements.append(Paragraph("Relatório de Rentabilidade por Modelo", title_style))
        elements.append(Spacer(1, 12))
        
        # Generate data
        rentabilidade_modelo = []
        modelos = importacoes.values('modelo').distinct()
        
        for modelo_dict in modelos:
            modelo = modelo_dict['modelo']
            modelo_importacoes = importacoes.filter(modelo=modelo)
            
            total_investido = sum([imp.custo_total_quantidade_brl for imp in modelo_importacoes])
            vendidos = modelo_importacoes.filter(status='vendido')
            total_vendido = sum([imp.preco_venda_unitario * imp.quantidade for imp in vendidos if imp.preco_venda_unitario])
            lucro_total = sum([imp.lucro_total for imp in vendidos if imp.lucro_total])
            
            rentabilidade_modelo.append({
                'modelo': modelo,
                'total_importacoes': modelo_importacoes.count(),
                'total_investido': total_investido,
                'lucro_total': lucro_total,
                'margem_media': (lucro_total / total_investido * 100) if total_investido > 0 else 0
            })
        
        # Create table
        data = [['Modelo', 'Importações', 'Investido (R$)', 'Lucro (R$)', 'Margem (%)']]
        for item in sorted(rentabilidade_modelo, key=lambda x: x['margem_media'], reverse=True):
            data.append([
                item['modelo'],
                str(item['total_importacoes']),
                f"R$ {item['total_investido']:,.2f}",
                f"R$ {item['lucro_total']:,.2f}",
                f"{item['margem_media']:.1f}%"
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        
    elif tipo_relatorio == 'status':
        # Status Report
        elements.append(Paragraph("Relatório de Status das Importações", title_style))
        elements.append(Spacer(1, 12))
        
        # Generate data
        status_report = []
        for status_choice in Importacao.STATUS_CHOICES:
            status_key = status_choice[0]
            status_importacoes = importacoes.filter(status=status_key)
            if status_importacoes.exists():
                total_valor = sum([imp.custo_total_quantidade_brl for imp in status_importacoes])
                total_unidades = sum([imp.quantidade for imp in status_importacoes])
                status_report.append({
                    'status': status_choice[1],
                    'count': status_importacoes.count(),
                    'total_unidades': total_unidades,
                    'total_valor': total_valor
                })
        
        # Create table
        data = [['Status', 'Importações', 'Unidades', 'Valor Total (R$)']]
        for item in status_report:
            data.append([
                item['status'],
                str(item['count']),
                str(item['total_unidades']),
                f"R$ {item['total_valor']:,.2f}"
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    
    elif tipo_relatorio == 'completo':
        # Complete Report
        elements.append(Paragraph("Relatório Completo de Importações", title_style))
        elements.append(Spacer(1, 12))
        
        # Summary statistics
        total_importacoes = importacoes.count()
        total_unidades = sum([imp.quantidade for imp in importacoes])
        total_investido = sum([imp.custo_total_quantidade_brl for imp in importacoes])
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Importações', str(total_importacoes)],
            ['Total de Unidades', str(total_unidades)],
            ['Total Investido', f"R$ {total_investido:,.2f}"]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Detailed importations
        elements.append(Paragraph("Detalhes das Importações", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        detail_data = [['Modelo', 'Capacidade', 'Grade', 'Qtd', 'Status', 'Custo Unit. (R$)']]
        for imp in importacoes.order_by('-created_at')[:20]:  # Last 20 imports
            detail_data.append([
                imp.modelo,
                f"{imp.capacidade_gb}GB",
                imp.grade,
                str(imp.quantidade),
                dict(Importacao.STATUS_CHOICES)[imp.status],
                f"R$ {imp.custo_total_py_brl:,.2f}"
            ])
        
        detail_table = Table(detail_data)
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(detail_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Return PDF response
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{tipo_relatorio}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response

@login_required
def export_relatorio_excel(request, tipo_relatorio):
    """Export reports to Excel"""
    if not EXPORT_AVAILABLE:
        messages.error(request, 'Bibliotecas de exportação não estão instaladas. Execute: pip install reportlab xlsxwriter matplotlib seaborn')
        return redirect('core:relatorios')
    
    user = request.user
    importacoes = Importacao.objects.filter(user=user)
    
    # Create Excel buffer
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    
    # Define formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D7E4BC',
        'border': 1
    })
    
    currency_format = workbook.add_format({
        'num_format': 'R$ #,##0.00',
        'border': 1
    })
    
    percent_format = workbook.add_format({
        'num_format': '0.0%',
        'border': 1
    })
    
    number_format = workbook.add_format({
        'border': 1
    })
    
    if tipo_relatorio == 'rentabilidade':
        worksheet = workbook.add_worksheet('Rentabilidade por Modelo')
        
        # Headers
        headers = ['Modelo', 'Total Importações', 'Total Unidades', 'Total Investido (R$)', 'Total Vendido (R$)', 'Lucro Total (R$)', 'Margem Média (%)']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data
        modelos = importacoes.values('modelo').distinct()
        row = 1
        
        for modelo_dict in modelos:
            modelo = modelo_dict['modelo']
            modelo_importacoes = importacoes.filter(modelo=modelo)
            
            total_investido = sum([imp.custo_total_quantidade_brl for imp in modelo_importacoes])
            vendidos = modelo_importacoes.filter(status='vendido')
            total_vendido = sum([imp.preco_venda_unitario * imp.quantidade for imp in vendidos if imp.preco_venda_unitario])
            lucro_total = sum([imp.lucro_total for imp in vendidos if imp.lucro_total])
            margem_media = (lucro_total / total_investido) if total_investido > 0 else 0
            
            worksheet.write(row, 0, modelo, number_format)
            worksheet.write(row, 1, modelo_importacoes.count(), number_format)
            worksheet.write(row, 2, sum([imp.quantidade for imp in modelo_importacoes]), number_format)
            worksheet.write(row, 3, float(total_investido), currency_format)
            worksheet.write(row, 4, float(total_vendido), currency_format)
            worksheet.write(row, 5, float(lucro_total), currency_format)
            worksheet.write(row, 6, margem_media, percent_format)
            row += 1
        
        # Auto-adjust column widths
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:C', 12)
        worksheet.set_column('D:F', 18)
        worksheet.set_column('G:G', 15)
    
    elif tipo_relatorio == 'completo':
        # Summary sheet
        summary_sheet = workbook.add_worksheet('Resumo')
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Importações', importacoes.count()],
            ['Total de Unidades', sum([imp.quantidade for imp in importacoes])],
            ['Total Investido (R$)', float(sum([imp.custo_total_quantidade_brl for imp in importacoes]))],
            ['Modelos Únicos', importacoes.values('modelo').distinct().count()],
            ['Grades Únicas', importacoes.values('grade').distinct().count()]
        ]
        
        for row, (metric, value) in enumerate(summary_data):
            if row == 0:
                summary_sheet.write(row, 0, metric, header_format)
                summary_sheet.write(row, 1, value, header_format)
            else:
                summary_sheet.write(row, 0, metric, number_format)
                if 'Investido' in metric:
                    summary_sheet.write(row, 1, value, currency_format)
                else:
                    summary_sheet.write(row, 1, value, number_format)
        
        summary_sheet.set_column('A:A', 20)
        summary_sheet.set_column('B:B', 15)
        
        # Detailed sheet
        detail_sheet = workbook.add_worksheet('Detalhes das Importações')
        
        detail_headers = [
            'Modelo', 'Capacidade (GB)', 'Grade', 'Quantidade', 'Status',
            'Valor EUA (USD)', 'Custo Total EUA (R$)', 'Custo Total PY (R$)',
            'Preço Venda (R$)', 'Lucro (R$)', 'Data Criação'
        ]
        
        for col, header in enumerate(detail_headers):
            detail_sheet.write(0, col, header, header_format)
        
        for row, imp in enumerate(importacoes.order_by('-created_at'), 1):
            detail_sheet.write(row, 0, imp.modelo, number_format)
            detail_sheet.write(row, 1, imp.capacidade_gb, number_format)
            detail_sheet.write(row, 2, imp.grade, number_format)
            detail_sheet.write(row, 3, imp.quantidade, number_format)
            detail_sheet.write(row, 4, dict(Importacao.STATUS_CHOICES)[imp.status], number_format)
            detail_sheet.write(row, 5, float(imp.valor_eua_unitario), currency_format)
            detail_sheet.write(row, 6, float(imp.custo_eua_brl), currency_format)
            detail_sheet.write(row, 7, float(imp.custo_total_py_brl), currency_format)
            detail_sheet.write(row, 8, float(imp.preco_venda_unitario or 0), currency_format)
            detail_sheet.write(row, 9, float(imp.lucro_unitario or 0), currency_format)
            detail_sheet.write(row, 10, imp.created_at.strftime('%d/%m/%Y %H:%M'), number_format)
        
        # Auto-adjust column widths
        detail_sheet.set_column('A:A', 15)
        detail_sheet.set_column('B:E', 12)
        detail_sheet.set_column('F:J', 18)
        detail_sheet.set_column('K:K', 16)
    
    workbook.close()
    buffer.seek(0)
    
    # Return Excel response
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="relatorio_{tipo_relatorio}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    return response

@login_required
def relatorio_rentabilidade(request):
    """Relatório detalhado de rentabilidade"""
    user = request.user
    importacoes = Importacao.objects.filter(user=user)
    
    # Detailed rentability analysis
    rentabilidade_detalhada = []
    
    for imp in importacoes:
        if imp.preco_venda_unitario and imp.lucro_unitario:
            rentabilidade_detalhada.append({
                'importacao': imp,
                'roi': (imp.lucro_unitario / imp.custo_total_py_brl * 100) if imp.custo_total_py_brl > 0 else 0,
                'markup': ((imp.preco_venda_unitario - imp.custo_total_py_brl) / imp.custo_total_py_brl * 100) if imp.custo_total_py_brl > 0 else 0
            })
    
    context = {
        'rentabilidade_detalhada': sorted(rentabilidade_detalhada, key=lambda x: x['roi'], reverse=True),
        'total_importacoes': importacoes.count(),
        'importacoes_vendidas': len(rentabilidade_detalhada)
    }
    
    return render(request, 'relatorios/rentabilidade_detalhada.html', context)
    pass

@login_required
def admin_panel(request):
    """Painel administrativo (apenas para admins)"""
    if request.user.role != 'admin':
        messages.error(request, 'Acesso negado.')
        return redirect('core:dashboard')
    
    # Estatísticas gerais do sistema
    total_usuarios = User.objects.count()
    total_importacoes_sistema = Importacao.objects.count()
    
    context = {
        'total_usuarios': total_usuarios,
        'total_importacoes_sistema': total_importacoes_sistema,
    }
    
    return render(request, 'admin/panel.html', context)

@login_required
def user_management(request):
    """Gestão de usuários (apenas para admins)"""
    if request.user.role != 'admin':
        messages.error(request, 'Acesso negado.')
        return redirect('core:dashboard')
    
    usuarios = User.objects.all().order_by('-date_joined')
    
    # Estatísticas dos usuários
    stats = {
        'total_usuarios': usuarios.count(),
        'usuarios_ativos': usuarios.filter(is_active=True).count(),
        'administradores': usuarios.filter(role='admin').count(),
        'usuarios_comuns': usuarios.filter(role='user').count(),
    }
    
    context = {
        'usuarios': usuarios,
        'stats': stats,
    }
    
    return render(request, 'admin/users.html', context)

@login_required
def user_create(request):
    """Criar novo usuário (apenas para admins)"""
    if request.user.role != 'admin':
        messages.error(request, 'Acesso negado.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Criar configuração padrão para o novo usuário
            ConfiguracaoPadrao.objects.create(user=user)
            messages.success(request, f'Usuário {user.username} criado com sucesso!')
            return redirect('core:user_management')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Criar Novo Usuário',
        'action': 'create'
    }
    
    return render(request, 'admin/user_form.html', context)

@login_required
def user_edit(request, user_id):
    """Editar usuário existente (apenas para admins)"""
    if request.user.role != 'admin':
        messages.error(request, 'Acesso negado.')
        return redirect('core:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuário {user.username} atualizado com sucesso!')
            return redirect('core:user_management')
    else:
        form = UserForm(instance=user)
    
    context = {
        'form': form,
        'user_obj': user,
        'title': f'Editar Usuário: {user.username}',
        'action': 'edit'
    }
    
    return render(request, 'admin/user_form.html', context)

@login_required
def user_delete(request, user_id):
    """Deletar usuário (apenas para admins)"""
    if request.user.role != 'admin':
        messages.error(request, 'Acesso negado.')
        return redirect('core:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    # Não permitir deletar o próprio usuário
    if user == request.user:
        messages.error(request, 'Você não pode deletar sua própria conta.')
        return redirect('core:user_management')
    
    # Não permitir deletar o último admin
    if user.role == 'admin' and User.objects.filter(role='admin').count() <= 1:
        messages.error(request, 'Não é possível deletar o último administrador do sistema.')
        return redirect('core:user_management')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Usuário {username} deletado com sucesso!')
        return redirect('core:user_management')
    
    context = {
        'user_obj': user,
        'title': f'Deletar Usuário: {user.username}'
    }
    
    return render(request, 'admin/user_delete.html', context)

@login_required
def user_toggle_status(request, user_id):
    """Ativar/desativar usuário (apenas para admins)"""
    if request.user.role != 'admin':
        messages.error(request, 'Acesso negado.')
        return redirect('core:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    # Não permitir desativar o próprio usuário
    if user == request.user:
        messages.error(request, 'Você não pode desativar sua própria conta.')
        return redirect('core:user_management')
    
    # Não permitir desativar o último admin
    if user.role == 'admin' and user.is_active and User.objects.filter(role='admin', is_active=True).count() <= 1:
        messages.error(request, 'Não é possível desativar o último administrador ativo do sistema.')
        return redirect('core:user_management')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'ativado' if user.is_active else 'desativado'
    messages.success(request, f'Usuário {user.username} {status} com sucesso!')
    
    return redirect('core:user_management')

@login_required
def configuracoes(request):
    """Configurações do usuário"""
    config, created = ConfiguracaoPadrao.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ConfiguracaoForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('core:configuracoes')
    else:
        form = ConfiguracaoForm(instance=config)
    
    context = {
        'form': form,
    }
    
    # Adicionar estatísticas para administradores
    if request.user.role == 'admin':
        context.update({
            'total_usuarios': User.objects.count(),
            'total_importacoes_sistema': Importacao.objects.count(),
        })
    
    return render(request, 'configuracoes/index.html', context)
