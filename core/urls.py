from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

app_name = 'core'

urlpatterns = [
    # Auth
    path('login/', LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Importações
    path('importacoes/', views.importacao_list, name='importacao_list'),
    path('importacoes/nova/', views.importacao_create, name='importacao_create'),
    path('importacoes/<int:pk>/', views.importacao_detail, name='importacao_detail'),
    path('importacoes/<int:pk>/editar/', views.importacao_update, name='importacao_update'),
    path('importacoes/<int:pk>/deletar/', views.importacao_delete, name='importacao_delete'),
    
    # HTMX endpoints
    path('htmx/calcular-custos/', views.calcular_custos_htmx, name='calcular_custos_htmx'),
    
    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/rentabilidade/', views.relatorio_rentabilidade, name='relatorio_rentabilidade'),
    
    # Export endpoints
    path('relatorios/export/pdf/<str:tipo_relatorio>/', views.export_relatorio_pdf, name='export_relatorio_pdf'),
    path('relatorios/export/excel/<str:tipo_relatorio>/', views.export_relatorio_excel, name='export_relatorio_excel'),
    
    # Admin (apenas para admins)
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/usuarios/', views.user_management, name='user_management'),
    path('admin-panel/usuarios/criar/', views.user_create, name='user_create'),
    path('admin-panel/usuarios/<int:user_id>/editar/', views.user_edit, name='user_edit'),
    path('admin-panel/usuarios/<int:user_id>/deletar/', views.user_delete, name='user_delete'),
    path('admin-panel/usuarios/<int:user_id>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),
    
    # Configurações
    path('configuracoes/', views.configuracoes, name='configuracoes'),
]
