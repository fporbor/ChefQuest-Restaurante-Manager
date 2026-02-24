from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import F, Sum, Count
from django.db.models import Prefetch

from .models import Empresa, Producto
from clientes.models import Reserva_Pedido
from .mixins import EmpresaEnSesionMixin, EmpresaStaffMixin

# Create your views here.
def login_empresa(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo")

        try:
            empresa = Empresa.objects.get(codigo=codigo, activo=True)
            request.session["empresa_id"] = empresa.id
            return redirect("dashboard_staff")

        except Empresa.DoesNotExist:
            messages.error(request, "Código inválido.")

    return render(request, "staff/login_empresa.html")

def logout_empresa(request):
    request.session.pop("empresa_id", None)
    return redirect("login_empresa")

class ProductoListView(LoginRequiredMixin,
                       PermissionRequiredMixin,
                       EmpresaEnSesionMixin,
                       EmpresaStaffMixin,
                       ListView):
    model = Producto
    permission_required = "staff.view_producto"
    template_name = "staff/producto_list.html"

class ProductoCreateView(LoginRequiredMixin,
                         PermissionRequiredMixin,
                         EmpresaEnSesionMixin,
                         CreateView):
    model = Producto
    fields = ["nombre", "descripcion", "precio",
              "coste", "stock", "activo", "categoria"]
    permission_required = "staff.add_producto"
    template_name = "staff/producto_form.html"
    success_url = reverse_lazy("producto_list")

    def form_valid(self, form):
        form.instance.empresa_id = self.request.session.get("empresa_id")
        return super().form_valid(form)

def confirmar_reserva(request, pk):
    reserva = get_object_or_404(Reserva_Pedido, pk=pk)

    for producto in reserva.productos.all():
        Producto.objects.filter(pk=producto.pk).update(
            stock=F("stock") - 1
        )

    reserva.estado = "CONFIRMADO"
    reserva.save()

    return redirect("lista_reservas_staff")

class EstadisticasView(LoginRequiredMixin,
                       EmpresaEnSesionMixin,
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
        )["total"]

        return context

class ProductoUpdateView(LoginRequiredMixin,
                         PermissionRequiredMixin,
                         EmpresaEnSesionMixin,
                         EmpresaStaffMixin,
                         UpdateView):
    model = Producto
    fields = ["nombre", "descripcion", "precio",
              "coste", "stock", "activo", "categoria"]

    permission_required = "staff.change_producto"
    template_name = "staff/producto_form.html"
    success_url = reverse_lazy("producto_list")

class ProductoDeleteView(LoginRequiredMixin,
                         PermissionRequiredMixin,
                         EmpresaEnSesionMixin,
                         EmpresaStaffMixin,
                         DeleteView):
    model = Producto
    permission_required = "staff.delete_producto"
    template_name = "staff/producto_confirm_delete.html"
    success_url = reverse_lazy("producto_list")

class ReservasEmpresaListView(LoginRequiredMixin,
                              PermissionRequiredMixin,
                              EmpresaEnSesionMixin,
                              ListView):
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