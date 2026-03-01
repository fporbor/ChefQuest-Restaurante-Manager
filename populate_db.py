# populate_db.py
import os
import django
import random
from datetime import datetime, timedelta

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
# Crear superuser de prueba si no existe
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
# Limpiamos datos existentes (sin borrar superusers)
# ---------------------------
print("Eliminando datos anteriores (sin superusers)...")
Reserva_Pedido.objects.all().delete()
Usuario.objects.filter(is_superuser=False).delete()
Producto.objects.all().delete()
Categoria.objects.all().delete()
Cupon.objects.all().delete()
Empresa.objects.all().delete()

# ---------------------------
# Creamos Cupones
# ---------------------------
print("Creando cupones...")
cupones = []
for i in range(3):
    c = Cupon.objects.create(
        nombre=f"CUPON{i+1}",
        descuento=random.choice([5, 10, 15, 20])
    )
    cupones.append(c)

# ---------------------------
# Creamos Empresas
# ---------------------------
print("Creando empresas...")
empresas = []
for i in range(3):
    e = Empresa.objects.create(
        nombre_comercial=f"Empresa{i+1}",
        contacto=f"contacto{i+1}@empresa.com",
        activo=True,
        codigo=str(1000 + i + 1)
    )
    empresas.append(e)

# ---------------------------
# Creamos Categorias
# ---------------------------
print("Creando categorias...")
categorias = []
for i in range(3):
    cat = Categoria.objects.create(
        nombre=f"Categoria{i+1}",
        cupon=random.choice(cupones)
    )
    categorias.append(cat)

# ---------------------------
# Creamos Productos
# ---------------------------
print("Creando productos...")
for i in range(10):
    Producto.objects.create(
        nombre=f"Producto{i+1}",
        descripcion=f"Descripción del producto {i+1}",
        precio=random.randint(5, 100),
        coste=random.randint(1, 50),
        stock=random.randint(10, 100),
        activo=True,
        empresa=random.choice(empresas),
        categoria=random.choice(categorias)
    )

# ---------------------------
# Creamos Usuarios (sin tocar superusers)
# ---------------------------
print("Creando usuarios...")
usuarios = []
for i in range(5):
    u = Usuario.objects.create_user(
        username=f"user{i+1}",
        password="password123",
        nombre_visible=f"Usuario{i+1}",
        email=f"user{i+1}@email.com",
        empresa=random.choice(empresas)
    )
    usuarios.append(u)

# ---------------------------
# Creamos Reservas/Pedidos
# ---------------------------
print("Creando reservas/pedidos...")
TIPOS = ["LOCAL", "COMIDA", "EVENTO"]
ESTADOS = ["PENDIENTE", "CONFIRMADO", "CANCELADO", "ENTREGADO"]

for i in range(10):
    r = Reserva_Pedido.objects.create(
        tipo=random.choice(TIPOS),
        fecha=datetime.now() + timedelta(days=random.randint(0, 10)),
        comensales=random.randint(1, 6),
        direccion=f"Calle {i+1}, Ciudad",
        notas=f"Notas de la reserva {i+1}",
        estado=random.choice(ESTADOS),
        cliente=random.choice(usuarios)
    )
    # Productos aleatorios
    productos = Producto.objects.order_by("?")[:random.randint(1, 3)]
    r.productos.set(productos)

print("Base de datos poblada correctamente ✅ (superusers intactos)")