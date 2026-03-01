# staff/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import Producto, Empresa


class ProductoFormStaff(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre",
            "descripcion",
            "precio",
            "coste",
            "stock",
            "activo",
            "categoria",
        ]

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if precio is None:
            return precio
        if precio < 0:
            raise ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_coste(self):
        coste = self.cleaned_data.get("coste")
        if coste is None:
            return coste
        if coste < 0:
            raise ValidationError("El coste no puede ser negativo.")
        return coste

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock is None:
            return stock
        if stock < 0:
            raise ValidationError("El stock no puede ser negativo.")
        return stock


class EmpresaRegistroForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ["nombre_comercial", "contacto", "codigo"]

    def clean_nombre_comercial(self):
        nombre = self.cleaned_data.get("nombre_comercial")
        if nombre is None:
            return nombre
        nombre = nombre.strip()
        if not nombre:
            raise ValidationError("El nombre comercial no puede estar vacío.")
        return nombre

    def clean_contacto(self):
        contacto = self.cleaned_data.get("contacto")
        if contacto is None:
            return contacto
        contacto = contacto.strip()
        if contacto == "":
            return None
        # validar formato de email si se proporciona
        try:
            validate_email(contacto)
        except ValidationError:
            raise ValidationError("El campo de contacto debe ser un email válido.")
        return contacto

    def clean_codigo(self):
        codigo = self.cleaned_data.get("codigo")
        if codigo is None:
            return codigo
        # normalizar a string y quitar espacios
        codigo = str(codigo).strip()
        if codigo == "":
            return None
        # comprobar unicidad excluyendo la instancia actual (útil en edición)
        qs = Empresa.objects.filter(codigo=codigo)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Ya existe una empresa con ese código.")
        return codigo

    def clean(self):
        """
        Validaciones cruzadas: si se proporciona código, asegurarse de que no esté vacío;
        si no se proporciona contacto, no forzar, pero avisar si ambos faltan.
        """
        cleaned = super().clean()
        nombre = cleaned.get("nombre_comercial")
        contacto = cleaned.get("contacto")
        codigo = cleaned.get("codigo")

        # nombre ya validado en clean_nombre_comercial, aquí solo comprobación adicional
        if not nombre:
            raise ValidationError("El nombre comercial es obligatorio.")

        # Si no hay contacto ni código, permitir creación pero advertir (o forzar según reglas)
        # Aquí no se fuerza, solo se deja la posibilidad de crear empresa mínima.
        return cleaned
