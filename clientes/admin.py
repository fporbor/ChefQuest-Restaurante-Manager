from django.contrib import admin
from .models import Usuario,Usuario_Perfil,Reserva_Pedido

# Register your models here.
"""
admin.site.register(Usuario)
admin.site.register(Usuario_Perfil)
admin.site.register(Reserva_Pedido)
"""
# -----------------------------
# Perfil Inline para Usuario
# -----------------------------
class UsuarioPerfilInline(admin.StackedInline):
    model = Usuario_Perfil
    can_delete = False
    verbose_name = "Perfil del usuario"
    verbose_name_plural = "Perfil del usuario"

# -----------------------------
# Admin personalizado para Usuario
# -----------------------------
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "nombre_visible",
        "email",
        "empresa",
        "is_staff",
        "is_active",
        "fecha_alta"
    )  # Columnas que se ven en la lista
    list_filter = ("is_staff", "is_active", "empresa")  # Filtros a la derecha
    search_fields = ("username", "nombre_visible", "email")  # Buscador
    ordering = ("username",)
    inlines = [UsuarioPerfilInline]  # Mostramos el perfil dentro del usuario
    filter_horizontal = ("groups", "user_permissions")  # Mejor UI para muchos grupos/permisos

# -----------------------------
# Admin para Usuario_Perfil
# -----------------------------
@admin.register(Usuario_Perfil)
class UsuarioPerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "direccion", "preferencias_de_comunicacion")
    search_fields = ("usuario__username", "direccion", "preferencias_de_comunicacion")

# -----------------------------
# Admin para Reserva_Pedido
# -----------------------------
@admin.register(Reserva_Pedido)
class ReservaPedidoAdmin(admin.ModelAdmin):
    list_display = (
        "tipo",
        "cliente",
        "empresa",
        "fecha",
        "estado",
        "comensales"
    )
    list_filter = ("tipo", "estado", "empresa")
    search_fields = ("cliente__username", "empresa__nombre_comercial", "direccion", "notas")
    ordering = ("-fecha",)
    filter_horizontal = ("productos",)  # Mejor UI para seleccionar múltiples productos