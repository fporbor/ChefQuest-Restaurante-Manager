from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser,Group,Permission
from django.db import models

from staff.models import Empresa, Producto


class Usuario(AbstractUser):
    nombre_visible = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)

    # Evita el conflicto de reverse accessor
    groups = models.ManyToManyField(
        Group,
        related_name='usuarios_grupo',  # <- nombre único
        blank=True,
        help_text='Grupos a los que pertenece el usuario.',
        verbose_name='grupos'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_permiso',  # <- nombre único
        blank=True,
        help_text='Permisos específicos de usuario.',
        verbose_name='permisos de usuario'
    )

    def __str__(self):
        return self.nombre_visible
class Usuario_Perfil(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    preferencias_de_comunicacion = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    observacion = models.TextField()

    def __str__(self):
        return self.usuario.nombre_visible

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
        tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
        fecha = models.DateTimeField()
        comensales = models.PositiveIntegerField()
        direccion = models.CharField(max_length=100)
        notas = models.TextField()
        estado = models.CharField(max_length=10, choices=ESTADOS_CHOICES)
        cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
        empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
        productos = models.ManyToManyField(Producto, related_name='reservas')