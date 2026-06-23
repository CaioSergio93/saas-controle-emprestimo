from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from .models import Emprestimo

# Desregistramos o padrão para customizar quem vê o quê
admin.site.unregister(User)
admin.site.unregister(Group)

# MÁGICA VISUAL SAAS: Esconde Usuários e Grupos de quem não é Superusuário
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = (
        'cliente', 
        'get_cartao_utilizado_exibir', 
        'get_valor_total', 
        'get_valor_parcela',
        'get_valor_faltante', 
        'parcelas_totais', 
        'get_parcelas_faltantes',
        'status_pagamento'
    )
    
    list_filter = ('cartao_utilizado', 'data_criacao')
    search_fields = ('cliente',)
    exclude = ('usuario_admin',)

    # Garante o isolamento dos dados por usuário
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario_admin=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.usuario_admin = request.user
        super().save_model(request, obj, form, change)

    # Formatações de exibição
    def get_cartao_utilizado_exibir(self, obj):
        return obj.get_cartao_utilizado_display()
    get_cartao_utilizado_exibir.short_description = "Cartão Utilizado"

    def get_valor_total(self, obj):
        return f"R$ {obj.valor_total}"
    get_valor_total.short_description = "Valor Total"

    def get_valor_parcela(self, obj):
        return f"R$ {obj.valor_parcela}"
    get_valor_parcela.short_description = "Valor da Parcela"

    def get_valor_faltante(self, obj):
        return f"R$ {obj.valor_faltante}"
    get_valor_faltante.short_description = "Valor Faltante"

    def get_parcelas_faltantes(self, obj):
        return f"{obj.parcelas_faltantes}x"
    get_parcelas_faltantes.short_description = "Parc. Faltantes"

    def status_pagamento(self, obj):
        if obj.parcelas_faltantes <= 0:
            return "✅ Quitado"
        return "⏳ Em Aberto"
    status_pagamento.short_description = "Status"