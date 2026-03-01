from django.contrib import admin
from .models import Empresa,Producto,Categoria,Cupon
# Register your models here.
"""
admin.site.register(Empresa)
admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(Cupon)
"""
# -----------------------------
# Admin para Empresa
# -----------------------------
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nombre_comercial", "contacto", "activo", "codigo")
    list_filter = ("activo",)
    search_fields = ("nombre_comercial", "contacto", "codigo")
    ordering = ("nombre_comercial",)

# -----------------------------
# Admin para Producto
# -----------------------------
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "categoria",
        "empresa",
        "precio",
        "precio_con_descuento",  # campo calculado
        "stock",
        "activo",
        "producto_del_dia",    
    )  
    list_filter = (
        "activo",
        "categoria",
        "empresa",
        "producto_del_dia",       # filtrable
    )
    search_fields = (
        "nombre",
        "descripcion",
        "empresa__nombre_comercial",
        "categoria__nombre",
    )
    ordering = ("nombre",)
    list_editable = ("activo", "producto_del_dia", "stock")  # editable rápido desde la lista

    def precio_con_descuento(self, obj):
        """Muestra el precio con descuento si tiene cupón"""
        if obj.categoria and obj.categoria.cupon:
            descuento = obj.categoria.cupon.descuento
            return round(obj.precio * (100 - descuento) / 100, 2)
        return obj.precio
    precio_con_descuento.short_description = "Precio con descuento (€)"

# -----------------------------
# Admin para Categoria
# -----------------------------
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cupon")
    list_filter = ("cupon",)
    search_fields = ("nombre", "cupon__nombre")
    ordering = ("nombre",)

# -----------------------------
# Admin para Cupon
# -----------------------------
@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descuento")
    search_fields = ("nombre",)
    ordering = ("nombre",)