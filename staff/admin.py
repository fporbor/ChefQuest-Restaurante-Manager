from django.contrib import admin
from .models import Empresa,Producto,Categoria,Cupon
# Register your models here.
admin.site.register(Empresa)
admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Cupon)