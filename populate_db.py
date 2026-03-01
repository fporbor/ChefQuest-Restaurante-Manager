# populate_db.py
import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone


# ---------------------------
# Configura Django
# ---------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chefquest.settings")
django.setup()

# ---------------------------
# Importamos modelos
# ---------------------------
from staff.models import Empresa, Producto, Categoria, Cupon
from clientes.models import Usuario, Reserva_Pedido

# ---------------------------
# Crear superuser de prueba
# ---------------------------
superuser_username = "eladminguay"
superuser_password = "eladmin123"
superuser_email = "admin@chefquest.com"

if not Usuario.objects.filter(username=superuser_username, is_superuser=True).exists():
    Usuario.objects.create_superuser(
        username=superuser_username,
        password=superuser_password,
        email=superuser_email,
        nombre_visible="Admin ChefQuest"
    )
    print(f"Superuser '{superuser_username}' creado ✅")
else:
    print(f"Superuser '{superuser_username}' ya existe, no se modifica")

# ---------------------------
# Limpiar datos (excepto superusers)
# ---------------------------
print("Eliminando datos anteriores...")
Reserva_Pedido.objects.all().delete()
Usuario.objects.filter(is_superuser=False).delete()
Producto.objects.all().delete()
Categoria.objects.all().delete()
Cupon.objects.all().delete()
Empresa.objects.all().delete()

# ---------------------------
# Crear Cupones
# ---------------------------
print("Creando cupones...")
cupones = [
    Cupon.objects.create(nombre="DESCUENTO5", descuento=5),
    Cupon.objects.create(nombre="DESCUENTO10", descuento=10),
    Cupon.objects.create(nombre="DESCUENTO15", descuento=15),
    Cupon.objects.create(nombre="DESCUENTO20", descuento=20),
]

# ---------------------------
# Crear Empresas (las que pediste)
# ---------------------------
print("Creando empresas...")

empresas_data = [
    ("Paco S.L", "contacto@pacosl.com"),
    ("Mercadona", "info@mercadona.com"),
    ("Alimentación Luna", "contacto@alimentacionluna.com"),
]

empresas = []
for i, (nombre, correo) in enumerate(empresas_data):
    empresas.append(
        Empresa.objects.create(
            nombre_comercial=nombre,
            contacto=correo,
            activo=True,
            codigo=str(2000 + i + 1)
        )
    )

# ---------------------------
# Crear Categorías reales
# ---------------------------
print("Creando categorías...")

categorias_data = [
    "Fruta",
    "Verdura",
    "Pescado",
    "Carne",
    "Bebidas",
    "Lácteos",
    "Panadería",
    "Congelados",
]

categorias = []
for nombre in categorias_data:
    categorias.append(
        Categoria.objects.create(
            nombre=nombre,
            cupon=random.choice(cupones)
        )
    )

# ---------------------------
# Productos reales por categoría
# ---------------------------
productos_por_categoria = {
    "Fruta": ["Manzana", "Plátano", "Naranja", "Fresa", "Pera"],
    "Verdura": ["Lechuga", "Tomate", "Zanahoria", "Cebolla", "Pimiento"],
    "Pescado": ["Salmón", "Merluza", "Atún", "Sardinas", "Bacalao"],
    "Carne": ["Pollo", "Ternera", "Cerdo", "Cordero", "Pavo"],
    "Bebidas": ["Agua", "Coca-Cola", "Zumo de Naranja", "Cerveza", "Vino"],
    "Lácteos": ["Leche", "Queso", "Yogur", "Mantequilla", "Kéfir"],
    "Panadería": ["Pan", "Croissant", "Bollo", "Baguette", "Donut"],
    "Congelados": ["Pizza congelada", "Verduras congeladas", "Helado", "Nuggets", "Patatas fritas"],
}

# ---------------------------
# Crear Productos
# ---------------------------
print("Creando productos...")

for categoria in categorias:
    lista = productos_por_categoria.get(categoria.nombre, [])
    for nombre_producto in lista:
        Producto.objects.create(
            nombre=nombre_producto,
            descripcion=f"{nombre_producto} fresco y de calidad",
            precio=random.randint(1, 20),
            coste=random.randint(1, 10),
            stock=random.randint(20, 200),
            activo=True,
            empresa=random.choice(empresas),
            categoria=categoria
        )

# ---------------------------
# Crear Usuarios normales
# ---------------------------
print("Creando usuarios...")

usuarios = []
for i in range(5):
    usuarios.append(
        Usuario.objects.create_user(
            username=f"user{i+1}",
            password="password123",
            nombre_visible=f"Usuario {i+1}",
            email=f"user{i+1}@email.com",
            empresa=random.choice(empresas)
        )
    )

# ---------------------------
# Crear Reservas/Pedidos
# ---------------------------
print("Creando reservas/pedidos...")

TIPOS = ["LOCAL", "COMIDA", "EVENTO"]
ESTADOS = ["PENDIENTE", "CONFIRMADO", "CANCELADO", "ENTREGADO"]

for i in range(10):
    r = Reserva_Pedido.objects.create(
        tipo=random.choice(TIPOS),
        fecha = timezone.now() + timedelta(days=random.randint(0, 10)),
        comensales=random.randint(1, 6),
        direccion=f"Calle {i+1}, Ciudad",
        notas=f"Notas de la reserva {i+1}",
        estado=random.choice(ESTADOS),
        cliente=random.choice(usuarios)
    )
    productos_random = Producto.objects.order_by("?")[:random.randint(1, 4)]
    r.productos.set(productos_random)

print("Base de datos poblada correctamente con empresas reales 🎉")
