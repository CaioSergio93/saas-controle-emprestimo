from django.contrib import admin
from django.urls import path
from controle import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('novo/', views.criar_emprestimo, name='criar_emprestimo'), # Nova Rota adicionada!
]

LOGOUT_REDIRECT_URL = '/admin/login/'
