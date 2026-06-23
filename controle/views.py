from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum  # Importa a ferramenta de soma do Django
from .models import Emprestimo
from decimal import Decimal
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

@login_required
def dashboard(request):
    # Filtra apenas os empréstimos do utilizador logado
    meus_emprestimos = Emprestimo.objects.filter(usuario_admin=request.user).order_by('-data_criacao')
    
    # Faz o cálculo dos totais dinâmicos baseados no utilizador logado
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

@login_required
def registrar_pagamento_parcela(request, pk):
    # Busca o empréstimo garantindo que pertence ao utilizador logado por segurança
    emprestimo = get_object_or_404(Emprestimo, pk=pk, usuario_admin=request.user)
    
    # Se ainda houver parcelas a serem pagas
    if emprestimo.parcelas_pagas < emprestimo.parcelas_totais:
        # Incrementar parcelas pagas
        emprestimo.parcelas_pagas += 1
        
        # Recalcular as parcelas faltantes se o seu modelo possuir esse campo persistido
        if hasattr(emprestimo, 'parcelas_faltantes') and emprestimo.parcelas_faltantes is not None:
            emprestimo.parcelas_faltantes = max(0, emprestimo.parcelas_totais - emprestimo.parcelas_pagas)
        
        # Subtrair o valor da parcela do valor faltante de forma segura
        valor_parcela = Decimal(str(emprestimo.valor_parcela or 0))
        valor_faltante_atual = Decimal(str(emprestimo.valor_faltante or 0))
        
        novo_faltante = valor_faltante_atual - valor_parcela
        
        # Se for a última parcela ou o valor zerar, seta tudo como quitado
        if novo_faltante <= 0 or emprestimo.parcelas_pagas >= emprestimo.parcelas_totais:
            emprestimo.valor_faltante = 0.00
            emprestimo.status = 'Quitado'
        else:
            emprestimo.valor_faltante = novo_faltante
            
        emprestimo.save()
        
    return redirect('dashboard')

def logar_usuario(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Usuário ou senha inválidos.")
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
        
    # Certifique-se de que o nome do ficheiro HTML abaixo coincide exatamente com o nome do ficheiro da sua tela de login
    return render(request, 'controle/login.html', {'form': form})