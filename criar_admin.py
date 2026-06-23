import os
import django

# Inicializa o ambiente do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

# DEFINA AQUI SEU USUÁRIO E SENHA DA SUA PREFERÊNCIA:
username = 'caio'
email = 'admin@email.com'
password = 'admin'  # Coloque uma senha forte

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print("👉 Superusuário criado com sucesso no Neon!")
else:
    print("👉 O usuário já existia no banco do Neon.")