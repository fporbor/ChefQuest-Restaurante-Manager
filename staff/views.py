from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import F, Count
from django.core.exceptions import PermissionDenied

from .models import Producto, Empresa
from clientes.models import Usuario
from clientes.models import Reserva_Pedido
from .mixins import EmpresaEnSesionMixin, EmpresaStaffMixin, UsuarioEmpresaRequiredMixin
from .forms import EmpresaRegistroForm


# ==============================
# LOGIN EMPRESA (FBV OBLIGATORIO)
# ==============================
def empresa_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not Empresa.objects.filter(contacto=request.user.email, activo=True).exists():
            return redirect("inicio")
        return view_func(request, *args, **kwargs)
    return wrapper
@login_required
@empresa_required
def login_empresa(request):
    if request.method == "POST":
        username = request.POST.get("username")
        codigo = request.POST.get("codigo")

        # Validamos que ambos campos existan
        if not username or not codigo:
            messages.error(request, "Debe introducir usuario y código de empresa.")
            return redirect("login_empresa")

        try:
            # Buscamos al usuario
            user = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no existe.")
            return redirect("login_empresa")

        # Validamos que el usuario tenga empresa y que el código coincida
        if not user.empresa or str(user.empresa.codigo) != codigo:
            messages.error(request, "Código de empresa incorrecto o usuario sin empresa asignada.")
            return redirect("login_empresa")

        # Guardamos la empresa en la sesión
        request.session["empresa_id"] = user.empresa.id
        messages.success(request, f"Sesión iniciada en {user.empresa.nombre_comercial}")
        return redirect("producto_list")

    return render(request, "staff/login_empresa.html")


@login_required
@empresa_required
def logout_empresa(request):
    # Eliminamos la empresa de la sesión
    request.session.pop("empresa_id", None)
    messages.info(request, "Sesión de empresa cerrada.")
    return redirect("login_empresa")


# ==============================
# CRUD PRODUCTOS (CBV OBLIGATORIO)
# ==============================



class ProductoListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,

    ListView,
):
    model = Producto
    permission_required = "staff.view_producto"
    template_name = "staff/producto_list.html"

    def get_queryset(self):
        empresa_id = self.request.session.get("empresa_id")

        if not empresa_id:
            raise PermissionDenied("No hay empresa activa en sesión.")

        return Producto.objects.filter(empresa_id=empresa_id)


class ProductoCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    EmpresaEnSesionMixin,
    UsuarioEmpresaRequiredMixin,
    CreateView,
):
    model = Producto
    fields = ["nombre", "descripcion", "precio",
              "coste", "stock", "activo", "categoria"]
    permission_required = "staff.add_producto"
    template_name = "staff/producto_form.html"
    success_url = reverse_lazy("staff:producto_list")

    def form_valid(self, form):
        empresa_id = self.request.session.get("empresa_id")

        if not empresa_id:
            raise PermissionDenied("No hay empresa activa en sesión.")

        form.instance.empresa_id = empresa_id
        return super().form_valid(form)


class ProductoUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    EmpresaEnSesionMixin,
    UsuarioEmpresaRequiredMixin,
    UpdateView,
):
    model = Producto
    fields = ["nombre", "descripcion", "precio",
              "coste", "stock", "activo", "categoria"]
    permission_required = "staff.change_producto"
    template_name = "staff/producto_form.html"
    success_url = reverse_lazy("staff:producto_list")

    def get_queryset(self):
        empresa_id = self.request.session.get("empresa_id")
        return Producto.objects.filter(empresa_id=empresa_id)

class ProductoDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    EmpresaEnSesionMixin,
    UsuarioEmpresaRequiredMixin,
    DeleteView,
):
    model = Producto
    permission_required = "staff.delete_producto"
    template_name = "staff/producto_confirm_delete.html"
    success_url = reverse_lazy("staff:producto_list")

    def get_queryset(self):
        empresa_id = self.request.session.get("empresa_id")
        return Producto.objects.filter(empresa_id=empresa_id)


# ==============================
# CRUD EMPRESAS (CBV OBLIGATORIO)
# ==============================

class EmpresaRegistroView(CreateView):
    model = Empresa
    form_class = EmpresaRegistroForm
    template_name = "staff/registro_empresa.html"
    success_url = reverse_lazy("login")

# ==============================
# LISTADO RESERVAS EMPRESA
# ==============================
class ReservasEmpresaListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    EmpresaEnSesionMixin,
    UsuarioEmpresaRequiredMixin,
    ListView,
):
    model = Reserva_Pedido
    permission_required = "clientes.view_reserva_pedido"
    template_name = "staff/reservas_empresa_list.html"

    def get_queryset(self):
        empresa_id = self.request.session.get("empresa_id")

        return (
            Reserva_Pedido.objects
            .filter(empresa_id=empresa_id)
            .select_related("cliente", "empresa")
            .prefetch_related("productos")
        )


# ==============================
# CONFIRMAR RESERVA (FBV)
# ==============================

@login_required
@empresa_required
def confirmar_reserva(request, pk):
    empresa_id = request.session.get("empresa_id")
    if not empresa_id:
        raise PermissionDenied
    empresa_id = request.session.get("empresa_id")

    reserva = get_object_or_404(
        Reserva_Pedido,
        pk=pk,
        empresa_id=empresa_id
    )

    if reserva.estado != "PENDIENTE":
        messages.error(request, "Solo se pueden confirmar reservas pendientes.")
        return redirect("staff:lista_reservas_staff")

    # Comprobar stock antes de confirmar
    for producto in reserva.productos.all():
        if producto.stock < 1:
            messages.error(request, f"No hay stock suficiente de {producto.nombre}.")
            return redirect("staff:lista_reservas_staff")

    # Restar stock
    for producto in reserva.productos.all():
        Producto.objects.filter(pk=producto.pk).update(
            stock=F("stock") - 1
        )

    reserva.estado = "CONFIRMADO"
    reserva.save()

    messages.success(request, "Reserva confirmada correctamente.")
    return redirect("staff:lista_reservas_staff")


# ==============================
# ESTADÍSTICAS
# ==============================

class EstadisticasView(LoginRequiredMixin,
                       UsuarioEmpresaRequiredMixin,
                       ListView):
    model = Reserva_Pedido
    template_name = "staff/estadisticas.html"

    def get_queryset(self):
        empresa_id = self.request.session.get("empresa_id")

        return (
            Reserva_Pedido.objects
            .filter(empresa_id=empresa_id)
            .annotate(total_productos=Count("productos"))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservas = self.get_queryset()

        context["total_reservas"] = reservas.count()

        context["total_confirmadas"] = reservas.filter(
            estado="CONFIRMADO"
        ).count()

        context["total_productos_vendidos"] = reservas.aggregate(
            total=Count("productos")
        )["total"] or 0

        return context