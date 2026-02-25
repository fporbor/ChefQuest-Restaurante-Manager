# staff/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import Producto


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