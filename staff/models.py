from django.db import models

class Cupon(models.Model):
    nombre = models.CharField(
        max_length=30,
        verbose_name="Nombre del cupón"
    )
    descuento = models.PositiveIntegerField(
        verbose_name="Descuento (%)"
    )
    
    class Meta:
        verbose_name = "Cupón"
        verbose_name_plural = "Cupones"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.descuento}%)"

class Categoria(models.Model):
    nombre = models.CharField(
        max_length=30,
        verbose_name="Nombre de la categoría"
    )
    # Si borramos el cupón asociado, la categoría no se elimina, solo se pone a NULL
    cupon = models.ForeignKey(
        Cupon,
        on_delete=models.SET_NULL,  # Evita eliminar la categoría si se borra el cupón
        null=True, 
        blank=True,
        related_name='categorias',
        related_query_name='categoria',
        verbose_name="Cupón asociado"
    )
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        if self.cupon:
            return f"{self.nombre} (Cupón: {self.cupon.nombre})"
        return self.nombre

class Empresa(models.Model):
    nombre_comercial = models.CharField(
        max_length=30,
        verbose_name="Nombre comercial"
    )
    contacto = models.EmailField(
        verbose_name="Correo de contacto"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="¿Activa?"
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código de empresa"
    )
    
    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['nombre_comercial']

    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.nombre_comercial} ({estado})"

class Producto(models.Model):
    nombre = models.CharField(
        max_length=30,
        verbose_name="Nombre del producto"
    )
    descripcion = models.TextField(
        verbose_name="Descripción"
    )
    precio = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Precio de venta"
    )
    coste = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Coste del producto"
    )
    stock = models.PositiveIntegerField(
        verbose_name="Cantidad en stock"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="¿Producto activo?"
    )
    
    # Si borramos la empresa, el producto no se elimina, solo se queda sin empresa
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.SET_NULL,  # Evita eliminar el producto si se borra la empresa
        null=True, 
        blank=True,
        related_name='productos',
        related_query_name='producto',
        verbose_name="Empresa"
    )
    
    # Si borramos la categoría, el producto no se elimina, solo queda sin categoría
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,  # Evita eliminar el producto si se borra la categoría
        null=True, 
        blank=True,
        related_name='productos',
        related_query_name='producto',
        verbose_name="Categoría"
    )
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        empresa_str = self.empresa.nombre_comercial if self.empresa else "Sin empresa"
        categoria_str = self.categoria.nombre if self.categoria else "Sin categoría"
        return f"{self.nombre} | {categoria_str} | {empresa_str} | Stock: {self.stock}"