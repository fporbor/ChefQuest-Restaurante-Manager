from django.contrib import admin
from .models import Usuario,Usuario_Perfil,Reserva_Pedido

# Register your models here.
admin.site.register(Usuario)
admin.site.register(Usuario_Perfil)
admin.site.register(Reserva_Pedido)