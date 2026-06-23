from django.contrib import admin
from django.urls import path
from controle import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('novo/', views.criar_emprestimo, name='criar_emprestimo'),
    path('emprestimo/<int:pk>/pagar-parcela/', views.registrar_pagamento_parcela, name='registrar_pagamento_parcela'),
    path('login/', views.logar_usuario, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
]

