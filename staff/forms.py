from django import forms
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

    # Validaciones de dominio
    def clean_precio(self):
        precio = self.cleaned_data["precio"]
        if precio < 0:
            raise ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_coste(self):
        coste = self.cleaned_data["coste"]
        if coste < 0:
            raise ValidationError("El coste no puede ser negativo.")
        return coste

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock < 0:
            raise ValidationError("El stock no puede ser negativo.")
        return stock

class ProductoFormCliente(forms.ModelForm):

    class Meta:
        model = Producto
        fields = [
            "nombre",
            "descripcion",
            "precio",
            "stock",
            "activo",
            "categoria",
        ]