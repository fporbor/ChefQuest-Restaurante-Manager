# clientes/forms.py
from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

from .models import Usuario, Usuario_Perfil, Reserva_Pedido
from staff.models import Producto, Empresa
from staff.forms import EmpresaRegistroForm


User = get_user_model()


class UsuarioRegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    es_empresa = forms.BooleanField(required=False, label="Registrarme como empresa")
    nombre_empresa = forms.CharField(required=False, label="Nombre de la empresa")

    class Meta:
        model = Usuario
        fields = [
            "username", "email", "nombre_visible", "telefono",
            "password1", "password2", "es_empresa", "nombre_empresa",
        ]

    def clean(self):
        cleaned_data = super().clean()
        es_empresa = cleaned_data.get("es_empresa")
        nombre_empresa = cleaned_data.get("nombre_empresa")

        if es_empresa:
            # Si nombre_empresa no viene en el form principal, buscar alternativa en POST/raw data
            if not nombre_empresa:
                # self.data contiene los datos crudos enviados (QueryDict)
                alt_nombre = None
                # posibles nombres que tu plantilla podría enviar
                for key in ("empresa_nombre_comercial", "nombre_comercial", "empresa_nombre"):
                    if self.data.get(key):
                        alt_nombre = self.data.get(key).strip()
                        break

                if alt_nombre:
                    # rellenar cleaned_data para que el resto del flujo lo vea
                    cleaned_data["nombre_empresa"] = alt_nombre
                else:
                    raise ValidationError("Si te registras como empresa debes indicar el nombre de la empresa.")

        return cleaned_data

    def _generar_codigo_unico(self):
        # Generador seguro de código numérico de 8 dígitos (ajusta longitud si lo deseas)
        for _ in range(10):
            codigo = get_random_string(8, allowed_chars='0123456789')
            if not Empresa.objects.filter(codigo=codigo).exists():
                return codigo
        raise ValidationError("No se pudo generar un código de empresa. Intenta de nuevo.")

    @transaction.atomic
    def save(self, commit=True):
        """
        Guarda únicamente el usuario y asigna grupos/flags.
        La creación del perfil y de la empresa debe hacerse desde la vista
        (UsuarioCreateView) para evitar duplicados en la relación OneToOne.
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()

            # asignar grupo y flags
            try:
                if self.cleaned_data.get("es_empresa"):
                    grupo = Group.objects.get(name="Empresas")
                    user.groups.add(grupo)
                    user.is_staff = True
                else:
                    grupo = Group.objects.get(name="Usuarios")
                    user.groups.add(grupo)
            except Group.DoesNotExist:
                pass
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
    username = forms.CharField(label="Usuario", max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Contraseña")
    codigo_empresa = forms.CharField(required=False, label="Código de empresa")
    es_empresa = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        # aceptar request si la vista lo pasa, sin romper si no viene
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.user = None
        self._auth_via_codigo = False

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        password = cleaned.get("password")
        codigo = cleaned.get("codigo_empresa")
        es_empresa = cleaned.get("es_empresa") in [True, 'True', 'true', '1', 'on']

        if not username:
            raise ValidationError("Usuario requerido.")

        # Primero intentar autenticar por contraseña (flujo normal)
        user = authenticate(username=username, password=password)
        if not user:
            # Si no se autentica por contraseña, dar error genérico
            raise ValidationError("Credenciales incorrectas.")

        # Si el usuario tiene empresa asociada (por ejemplo user.empresa o perfil)
        empresa_obj = None
        # Ajusta la comprobación según tu modelo: user.empresa o Usuario_Perfil.empresa
        if hasattr(user, "empresa") and user.empresa:
            empresa_obj = user.empresa
        else:
            # si usas perfil con FK a empresa:
            perfil = getattr(user, "usuario_perfil", None) or getattr(user, "perfil", None)
            if perfil and getattr(perfil, "empresa", None):
                empresa_obj = perfil.empresa

        # Caso: usuario tiene empresa asociada
        if empresa_obj:
            # Si marca es_empresa → validar código (no se exige contraseña extra)
            if es_empresa:
                if not codigo:
                    raise ValidationError("Debes introducir el código de empresa.")
                if str(empresa_obj.codigo) != str(codigo):
                    raise ValidationError("Código de empresa incorrecto.")
                # todo OK: autenticado por contraseña + código (o solo código si quieres)
                self.user = user
                self._auth_via_codigo = True
                return cleaned

            # Si NO marca es_empresa y NO proporciona código → mostramos el mensaje solicitado
            if not es_empresa and not codigo:
                raise ValidationError(
                    "Creemos que eres una empresa: marca 'Soy empresa' e introduce el código de empresa."
                )

            # Si no marca pero sí proporciona código (flujo mixto): validar código
            if codigo:
                if str(empresa_obj.codigo) != str(codigo):
                    raise ValidationError("Código de empresa incorrecto.")
                self.user = user
                self._auth_via_codigo = True
                return cleaned

        # Usuario sin empresa asociada o sin conflicto → login normal
        self.user = user
        self._auth_via_codigo = False
        return cleaned
