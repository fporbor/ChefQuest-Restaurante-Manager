# staff/views.py
from functools import wraps
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
from .utils import get_empresa_id_from_user
from .decorators import empresa_required
from django.contrib.auth import login

# ==============================
# LOGIN EMPRESA (FBV)
# ==============================
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

        # Intentar obtener la empresa asociada al usuario (FK directa)
        empresa_obj = getattr(user, "empresa", None)

        if not empresa_obj:
            messages.error(request, "El usuario no tiene empresa asignada.")
            return redirect("login_empresa")

        # Validamos que la empresa esté activa y el código coincida
        if not empresa_obj.activo or str(empresa_obj.codigo) != str(codigo):
            messages.error(request, "Código de empresa incorrecto o empresa inactiva.")
            return redirect("login_empresa")

        # Guardamos la empresa en la sesión
        request.session["empresa_id"] = empresa_obj.id
        messages.success(request, f"Sesión iniciada en {empresa_obj.nombre_comercial}")
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
# CRUD PRODUCTOS (CBV)
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
        # Priorizar empresa en sesión
        empresa_id = self.request.session.get("empresa_id")

        # Si no hay empresa en sesión, intentar obtenerla desde el usuario
        if not empresa_id:
            empresa_id = get_empresa_id_from_user(self.request.user)
            if empresa_id:
                # fijar en sesión para próximas peticiones
                self.request.session["empresa_id"] = empresa_id

        if not empresa_id:
            raise PermissionDenied("No hay empresa activa en sesión ni asociada al usuario.")

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
            # intentar obtener desde usuario
            empresa_id = get_empresa_id_from_user(self.request.user)
            if empresa_id:
                self.request.session["empresa_id"] = empresa_id

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
        empresa_id = self.request.session.get("empresa_id") or get_empresa_id_from_user(self.request.user)
        if not empresa_id:
            raise PermissionDenied("No hay empresa activa en sesión.")
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
        empresa_id = self.request.session.get("empresa_id") or get_empresa_id_from_user(self.request.user)
        if not empresa_id:
            raise PermissionDenied("No hay empresa activa en sesión.")
        return Producto.objects.filter(empresa_id=empresa_id)


# ==============================
# CRUD EMPRESAS (CBV)
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
        empresa_id = self.request.session.get("empresa_id") or get_empresa_id_from_user(self.request.user)

        if not empresa_id:
            raise PermissionDenied("No hay empresa activa en sesión.")

        # Filtrar por cliente__empresa (el usuario cliente tiene FK a Empresa)
        return (
            Reserva_Pedido.objects
            .filter(cliente__empresa_id=empresa_id)
            .select_related("cliente")
            .prefetch_related("productos")
        )


# ==============================
# CONFIRMAR RESERVA (FBV)
# ==============================

@login_required
@empresa_required
def confirmar_reserva(request, pk):
    empresa_id = request.session.get("empresa_id") or get_empresa_id_from_user(request.user)
    if not empresa_id:
        raise PermissionDenied

    reserva = get_object_or_404(Reserva_Pedido, pk=pk)

    # Validar que la reserva pertenece a la empresa activa (por cliente.empresa)
    if not reserva.cliente or not getattr(reserva.cliente, "empresa", None) or reserva.cliente.empresa.id != empresa_id:
        raise PermissionDenied("No tienes permisos sobre esta reserva.")

    if reserva.estado != "PENDIENTE":
        messages.error(request, "Solo se pueden confirmar reservas pendientes.")
        return redirect("staff:lista_reservas_staff")

    # Comprobar stock solo de los productos que pertenecen a la empresa activa
    productos_empresa = reserva.productos.filter(empresa_id=empresa_id)
    for producto in productos_empresa:
        if producto.stock < 1:
            messages.error(request, f"No hay stock suficiente de {producto.nombre}.")
            return redirect("staff:lista_reservas_staff")

    # Restar stock solo de esos productos
    for producto in productos_empresa:
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

    def get_empresa_id(self):
        # Prioriza empresa en sesión; si no, usa user.empresa (FK)
        empresa_id = self.request.session.get("empresa_id")
        if empresa_id:
            return empresa_id
        user_empresa = getattr(self.request.user, "empresa", None)
        if user_empresa:
            # fijar en sesión para próximas peticiones
            self.request.session["empresa_id"] = user_empresa.id
            return user_empresa.id
        return None

    def get_queryset(self):
        empresa_id = self.get_empresa_id()

        if not empresa_id:
            # Opción B: redirigir al login_empresa con mensaje
            messages.error(self.request, "No tienes una empresa asociada. Inicia sesión en una empresa para ver estadísticas.")
            return Reserva_Pedido.objects.none()

        return (
            Reserva_Pedido.objects
            .filter(cliente__empresa_id=empresa_id)
            .select_related("cliente")
            .prefetch_related("productos")
            .annotate(total_productos=Count("productos"))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservas = self.get_queryset()

        context["total_reservas"] = reservas.count()
        context["total_confirmadas"] = reservas.filter(estado="CONFIRMADO").count()
        context["total_productos_vendidos"] = reservas.aggregate(total=Count("productos"))["total"] or 0

        # Indicar en contexto si no hay empresa para que la plantilla muestre CTA
        context["empresa_id"] = self.request.session.get("empresa_id")
        return context
