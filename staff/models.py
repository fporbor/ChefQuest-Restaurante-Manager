from django.db import models

# Create your models here.
class Empresa(models.Model):
    nombre_comercial = models.CharField(max_length=30)
    contacto = models.EmailField()
    activo = models.BooleanField(default=True)
    def __str__(self):
        return self.nombre_comercial

class Producto(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=5, decimal_places=2)
    coste = models.DecimalField(max_digits=5, decimal_places=2)
    stock = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre_comercial}"

class Categoria(models.Model):
    nombre = models.CharField(max_length=30)
    cupon = models.ForeignKey('Cupon', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.nombre

class Cupon(models.Model):
    nombre = models.CharField(max_length=30)
    descuento = models.PositiveIntegerField()
    def __str__(self):
        return self.nombre