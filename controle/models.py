from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType


class Emprestimo(models.Model):
    OPCOES_BANCOS = [
        ('Nubank', 'Nubank'),
        ('Banco Inter', 'Banco Inter'),
        ('C6 Bank', 'C6 Bank'),
        ('Itaú', 'Itaú'),
        ('Bradesco', 'Bradesco'),
        ('Santander', 'Santander'),
        ('Caixa', 'Caixa'),
        ('Banco do Brasil', 'Banco do Brasil'),
        ('Outro', 'Outro (Especificar no nome)'),
    ]

    # CAMPO SAAS: Vincula este empréstimo a uma conta específica
    usuario_admin = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Dono do Registro")

    # Identificação do usuário e cartão
    cliente = models.CharField(max_length=150, verbose_name="Nome do Cliente")
    cartao_utilizado = models.CharField(
        max_length=100, 
        choices=OPCOES_BANCOS, 
        default='Nubank',
        verbose_name="Cartão Utilizado"
    )
    
    # Valores informados manualmente por você
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total (R$)")
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Valor de Cada Parcela (R$)")
    valor_faltante = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Valor Faltante (R$)")
    
    # Parcelas informadas manualmente por você
    parcelas_totais = models.IntegerField(verbose_name="Quantidade de Parcelas Totais")
    parcelas_pagas = models.IntegerField(default=0, verbose_name="Quantidade de Parcelas Pagas")
    parcelas_faltantes = models.IntegerField(default=0, verbose_name="Quantidade de Parcelas Faltantes")
    
    # Datas e Status
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data do Empréstimo")

    def __str__(self):
        return f"{self.cliente} - {self.get_cartao_utilizado_display()} (R$ {self.valor_total})"

    class Meta:
        verbose_name = "Empréstimo"
        verbose_name_plural = "Empréstimos"

# SIGNAL: Automatiza a criação do grupo e inserção do usuário
@receiver(post_save, sender=User)
def configurar_usuario_saas(sender, instance, created, **kwargs):
    if created:
        # 1. Garante que o usuário consegue logar no painel Admin (Staff Status)
        if not instance.is_superuser and not instance.is_staff:
            instance.is_staff = True
            instance.save()

        # 2. Busca ou cria o Grupo "Clientes SaaS"
        grupo_saas, _ = Group.objects.get_or_create(name='Clientes SaaS')

        # 3. Dá as permissões do modelo Emprestimo para este grupo
        content_type = ContentType.objects.get_for_model(Emprestimo)
        codenames = ['add_emprestimo', 'change_emprestimo', 'delete_emprestimo', 'view_emprestimo']
        
        for codename in codenames:
            permissao = Permission.objects.get(codename=codename, content_type=content_type)
            grupo_saas.permissions.add(permissao)

        # 4. Adiciona o usuário recém-criado ao grupo
        instance.groups.add(grupo_saas)