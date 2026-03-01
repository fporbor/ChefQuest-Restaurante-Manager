from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from staff.models import Empresa, Producto

# -----------------------
# Modelo de usuario
# -----------------------
class Usuario(AbstractUser):
    nombre_visible = models.CharField(
        max_length=100,
        verbose_name="Nombre visible"
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono"
    )
    fecha_alta = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de alta"
    )

    # Evita conflicto de reverse accessor con grupos
    groups = models.ManyToManyField(
        Group,
        related_name='usuarios_grupo',  # nombre único para evitar conflictos
        blank=True,
        help_text='Grupos a los que pertenece el usuario.',
        verbose_name='Grupos'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_permiso',  # nombre único para evitar conflictos
        blank=True,
        help_text='Permisos específicos de usuario.',
        verbose_name='Permisos de usuario'
    )

    # Relación con empresa
    empresa = models.ForeignKey(
        "Empresa",
        on_delete=models.CASCADE,  # SI borras la empresa, borramos al usuario.
        null=True,
        blank=True,
        verbose_name="Empresa"
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ['username']

    def __str__(self):
        return f"{self.nombre_visible} ({self.username})"

# -----------------------
# Perfil de usuario
# -----------------------
class Usuario_Perfil(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,  # Si borramos el usuario, borramos su perfil automáticamente
        verbose_name="Usuario"
    )
    preferencias_de_comunicacion = models.CharField(
        max_length=100,
        verbose_name="Preferencias de comunicación"
    )
    direccion = models.CharField(
        max_length=100,
        verbose_name="Dirección"
    )
    observacion = models.TextField(
        verbose_name="Observaciones"
    )

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self):
        return f"{self.usuario.nombre_visible} - Perfil"

# -----------------------
# Reservas y pedidos
# -----------------------
class Reserva_Pedido(models.Model):
    TIPO_CHOICES = [
        ('LOCAL', 'Reserva en local'),
        ('COMIDA', 'Pedido de comida'),
        ('EVENTO', 'Evento')
    ]
    ESTADOS_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('CANCELADO', 'Cancelado'),
        ('ENTREGADO', 'Entregado')
    ]

    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        verbose_name="Tipo"
    )
    fecha = models.DateTimeField(
        verbose_name="Fecha y hora"
    )
    comensales = models.PositiveIntegerField(
        verbose_name="Número de comensales"
    )
    direccion = models.CharField(
        max_length=100,
        verbose_name="Dirección"
    )
    notas = models.TextField(
        verbose_name="Notas adicionales",
        blank=True
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADOS_CHOICES,
        verbose_name="Estado"
    )

    # Relación con cliente
    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,  # <- Si borramos el usuario, borramos sus reservas automáticamente
        null=True,
        blank=True,
        verbose_name="Cliente"
    )

    # Relación con empresa
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,  # Si borramos la empresa, borramos las reservas asociadas
        null=True,
        blank=True,
        verbose_name="Empresa"
    )

    # Productos asociados a esta reserva
    productos = models.ManyToManyField(
        Producto,
        related_name='reservas',
        verbose_name="Productos"
    )

    class Meta:
        verbose_name = "Reserva / Pedido"
        verbose_name_plural = "Reservas / Pedidos"
        ordering = ['-fecha']  # ordenadas de la más reciente a la más antigua

    def __str__(self):
        cliente_str = self.cliente.nombre_visible if self.cliente else "Cliente desconocido"
        return f"{self.tipo} - {cliente_str} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"