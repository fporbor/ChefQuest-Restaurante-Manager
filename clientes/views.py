from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required
from django.views import View

from .models import Usuario, Usuario_Perfil, Reserva_Pedido
from .forms import UsuarioRegistroForm, UsuarioPerfilForm, ReservaPedidoForm, LoginEmpresaForm
from staff.models import Producto, Empresa
from staff.mixins import ClientePropietarioMixin


# Create your views here.
def inicio(request):
    productos_activos = Producto.objects.filter(activo=True)
    
    # Productos del día
    carta_del_dia = productos_activos.filter(producto_del_dia=True)
    
    if not carta_del_dia.exists():
        carta_del_dia = None  # Indicamos que no hay carta del día

    productos = []
    for p in productos_activos:
        descuento = p.categoria.cupon.descuento if p.categoria and p.categoria.cupon else 0
        precio_final = round(p.precio * (100 - descuento) / 100, 2)
        productos.append({
            'nombre': p.nombre,
            'descripcion': p.descripcion,
            'precio': p.precio,
            'precio_descuento': precio_final,
            'categoria': p.categoria.nombre if p.categoria else "Sin categoría",
            'empresa': p.empresa.nombre_comercial if p.empresa else "Sin empresa",
        })

    return render(request, "clientes/inicio.html", {
        "productos": productos,
        "carta_del_dia": carta_del_dia,
    })

class UsuarioCreateView(CreateView):
    model = Usuario
    form_class = UsuarioRegistroForm
    template_name = "clientes/registro.html"
    success_url = reverse_lazy("clientes:inicio")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["perfil_form"] = UsuarioPerfilForm(
            self.request.POST or None
        )
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        perfil_form = context["perfil_form"]

        if perfil_form.is_valid():
            usuario = form.save()
            perfil = perfil_form.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

            login(self.request, usuario)
            return redirect(self.success_url)

        return self.form_invalid(form)

class UsuarioLoginView(View):
    template_name = "registration/login.html"

    def get(self, request):
        form = LoginEmpresaForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginEmpresaForm(request.POST)

        if form.is_valid():
            login(request, form.user)

            # Guardar empresa en sesión si tiene
            if form.user.empresa:
                request.session["empresa_id"] = form.user.empresa.id

            return redirect("inicio")

        return render(request, self.template_name, {"form": form})


class UsuarioLogoutView(LogoutView):
    next_page = reverse_lazy("clientes:inicio")

class ReservaPedidoCreateView(LoginRequiredMixin, CreateView):
    model = Reserva_Pedido
    form_class = ReservaPedidoForm
    template_name = "clientes/reserva_form.html"
    success_url = reverse_lazy("clientes:mis_reservas")

    SESSION_KEY = "reserva_en_construccion"

    def get_initial(self):
        """
        Cargar datos guardados en sesión si existen.
        """
        initial = super().get_initial()
        datos = self.request.session.get(self.SESSION_KEY)

        if datos:
            initial.update(datos)

        return initial

    def form_invalid(self, form):
        """
        Guardar datos en sesión si el formulario es inválido.
        """
        datos = self.request.POST.dict()
        datos.pop("csrfmiddlewaretoken", None)

        # productos es ManyToMany → guardar lista
        datos["productos"] = self.request.POST.getlist("productos")

        self.request.session[self.SESSION_KEY] = datos

        messages.warning(
            self.request,
            "Tu reserva se ha guardado temporalmente en sesión."
        )

        return super().form_invalid(form)

    def form_valid(self, form):
        """
        Guardar reserva definitiva y limpiar sesión.
        """
        form.instance.cliente = self.request.user
        form.instance.empresa_id = self.request.session.get("empresa_id")
        form.instance.estado = "PENDIENTE"

        response = super().form_valid(form)

        # Limpiar sesión
        if self.SESSION_KEY in self.request.session:
            del self.request.session[self.SESSION_KEY]

        messages.success(self.request, "Reserva creada correctamente.")

        return response

class ReservaPedidoUpdateView(LoginRequiredMixin,
                               ClientePropietarioMixin,
                               UpdateView):
    model = Reserva_Pedido
    form_class = ReservaPedidoForm
    template_name = "clientes/reserva_form.html"
    success_url = reverse_lazy("clientes:mis_reservas")

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        return super().form_valid(form)

class MisReservasListView(LoginRequiredMixin,
                          ClientePropietarioMixin,
                          ListView):
    model = Reserva_Pedido
    template_name = "clientes/mis_reservas.html"

class ReservaDetailView(LoginRequiredMixin,
                        ClientePropietarioMixin,
                        DetailView):
    model = Reserva_Pedido
    template_name = "clientes/reserva_detail.html"

@login_required
def cancelar_reserva(request, pk):
    reserva = get_object_or_404(
        Reserva_Pedido,
        pk=pk,
        cliente=request.user
    )

    if reserva.estado == "CANCELADO":
        messages.warning(request, "La reserva ya estaba cancelada.")
        return redirect("clientes:mis_reservas")

    reserva.estado = "CANCELADO"
    reserva.save()

    messages.success(request, "Reserva cancelada.")
    return redirect("clientes:mis_reservas")


@login_required
def limpiar_reserva_sesion(request):
    request.session.pop("reserva_en_construccion", None)
    messages.info(request, "Reserva temporal eliminada.")
    return redirect("reserva_create")
def cambiar_tema(request):
    """
    Guarda la preferencia de tema en una cookie.
    """
    tema = request.GET.get("tema", "claro")

    response = redirect("inicio")
    response.set_cookie(
        "tema",
        tema,
        max_age=60 * 60 * 24 * 30  # 30 días
    )

    return response





class CustomLoginView(LoginView):
    template_name = "clientes/login.html"

    def get_success_url(self):
        user = self.request.user

        # Si el email pertenece a empresa activa → ir a staff
        if Empresa.objects.filter(contacto=user.email, activo=True).exists():
            return reverse_lazy("staff:producto_list")

        # Usuario normal → inicio público
        return reverse_lazy("inicio")