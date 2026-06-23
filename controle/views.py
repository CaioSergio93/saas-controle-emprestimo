from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum # Importa a ferramenta de soma do Django
from .models import Emprestimo

@login_required
def dashboard(request):
    meus_emprestimos = Emprestimo.objects.filter(usuario_admin=request.user).order_by('-data_criacao')
    
    # Faz o cálculo dos totais dinâmicos baseados no usuário logado
    total_carteira = meus_emprestimos.aggregate(Sum('valor_total'))['valor_total__sum'] or 0.00
    total_faltante = meus_emprestimos.aggregate(Sum('valor_faltante'))['valor_faltante__sum'] or 0.00

    context = {
        'emprestimos': meus_emprestimos,
        'total_carteira': f"{total_carteira:,.2f}",
        'total_faltante': f"{total_faltante:,.2f}",
    }
    return render(request, 'controle/dashboard.html', context)

@login_required
def criar_emprestimo(request):
    if request.method == 'POST':
        Emprestimo.objects.create(
            usuario_admin=request.user,
            cliente=request.POST.get('cliente'),
            cartao_utilizado=request.POST.get('cartao_utilizado'),
            valor_total=request.POST.get('valor_total'),
            valor_parcela=request.POST.get('valor_parcela'),
            valor_faltante=request.POST.get('valor_faltante'),
            parcelas_totais=request.POST.get('parcelas_totais'),
            parcelas_pagas=request.POST.get('parcelas_pagas'),
            parcelas_faltantes=request.POST.get('parcelas_faltantes'),
        )
        return redirect('dashboard')

    return render(request, 'controle/criar_emprestimo.html', {'opcoes_bancos': Emprestimo.OPCOES_BANCOS})