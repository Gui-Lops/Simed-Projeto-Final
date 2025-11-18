
from django.contrib import admin
# Importe todos os modelos que você quer ver na área admin
from .models import Perfil, Consulta, Medicamento

# Django vai mostrar uma interface para cada modelo registrado aqui
admin.site.register(Perfil)
admin.site.register(Consulta)
admin.site.register(Medicamento) # <--- Adicione esta linha
# Register your models here.
