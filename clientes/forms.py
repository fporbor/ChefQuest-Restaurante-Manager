from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.contrib.auth import authenticate

from .models import Usuario, Usuario_Perfil, Reserva_Pedido

from staff.models import Producto, Empresa

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from staff.models import Empresa
from .models import Usuario


class UsuarioRegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    es_empresa = forms.BooleanField(
        required=False,
        label="Registrarme como empresa"
    )

    nombre_empresa = forms.CharField(
        required=False,
        label="Nombre de la empresa"
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "email",
            "nombre_visible",
            "telefono",
            "password1",
            "password2",
            "es_empresa",
            "nombre_empresa",
        ]

    def clean(self):
        cleaned_data = super().clean()
        es_empresa = cleaned_data.get("es_empresa")
        nombre_empresa = cleaned_data.get("nombre_empresa")

        if es_empresa and not nombre_empresa:
            raise ValidationError(
                "Debes indicar el nombre de la empresa."
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()

            # 🔥 AQUÍ está el cambio automático
            if self.cleaned_data.get("es_empresa"):
                grupo = Group.objects.get(name="Empresas")
                user.groups.add(grupo)
                user.is_staff = True  # necesario para permisos staff
            else:
                grupo = Group.objects.get(name="Usuarios")
                user.groups.add(grupo)

            user.save()

        return user
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

class LoginEmpresaForm(forms.Form):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(widget=forms.PasswordInput)
    codigo_empresa = forms.CharField(
        required=False,
        label="Código Empresa"
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        codigo_empresa = cleaned_data.get("codigo_empresa")

        user = authenticate(username=username, password=password)

        if not user:
            raise ValidationError("Credenciales incorrectas.")

        # Si tiene empresa asociada
        if user.empresa:
            if not codigo_empresa:
                raise ValidationError(
                    "Debes introducir el código de empresa."
                )

            if user.empresa.codigo != codigo_empresa:
                raise ValidationError(
                    "Código de empresa incorrecto."
                )

        self.user = user
        return cleaned_data