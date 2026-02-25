from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from datetime import timedelta

from .models import Usuario, Usuario_Perfil, Reserva_Pedido
from staff.models import Producto

class UsuarioRegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Usuario
        fields = [
            "username",
            "email",
            "nombre_visible",
            "telefono",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"]

        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con ese email.")

        return email


class UsuarioPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario_Perfil
        fields = [
            "preferencias_de_comunicacion",
            "direccion",
            "observacion",
        ]

class ReservaPedidoForm(forms.ModelForm):

    class Meta:
        model = Reserva_Pedido
        fields = [
            "tipo",
            "fecha",
            "comensales",
            "direccion",
            "notas",
            "productos",
        ]
        widgets = {
            "fecha": forms.DateTimeInput(attrs={"type": "datetime-local"})
        }

    def clean_fecha(self):
        fecha = self.cleaned_data.get("fecha")

        if not fecha:
            return fecha

        if fecha <= timezone.now():
            raise ValidationError("La fecha debe ser futura.")

        return fecha

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        fecha = cleaned_data.get("fecha")
        comensales = cleaned_data.get("comensales")
        productos = cleaned_data.get("productos")

        if tipo == "LOCAL":
            if not comensales or comensales < 1:
                raise ValidationError(
                    "Una reserva en local debe tener al menos 1 comensal."
                )

        if tipo == "COMIDA":
            if not productos or productos.count() == 0:
                raise ValidationError(
                    "Un pedido de comida debe incluir productos."
                )

        if tipo == "EVENTO":
            if not comensales or comensales < 5:
                raise ValidationError(
                    "Un evento requiere al menos 5 comensales."
                )

            if fecha and fecha <= timezone.now() + timedelta(hours=48):
                raise ValidationError(
                    "Los eventos requieren al menos 48h de antelación."
                )

        return cleaned_data

    def clean_productos(self):
        productos = self.cleaned_data.get("productos")

        if not productos:
            return productos

        for producto in productos:
            if not producto.activo:
                raise ValidationError(
                    f"{producto.nombre} no está disponible."
                )

            if producto.stock < 1:
                raise ValidationError(
                    f"{producto.nombre} no tiene stock suficiente."
                )

        return productos