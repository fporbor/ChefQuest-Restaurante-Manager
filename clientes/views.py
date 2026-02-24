from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.db import transaction
from django.contrib import messages

from .models import Usuario, Usuario_Perfil, Reserva_Pedido
from .forms import UsuarioRegistroForm, UsuarioPerfilForm, ReservaPedidoForm
from staff.models import Producto
from staff.mixins import ClientePropietarioMixin

# Create your views here.
def inicio(request):
    productos = Producto.objects.filter(activo=True)
    return render(request, "clientes/inicio.html", {
        "productos": productos
    })

class UsuarioCreateView(CreateView):
    model = Usuario
    form_class = UsuarioRegistroForm
    template_name = "clientes/registro.html"
    success_url = reverse_lazy("inicio")

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

class UsuarioLoginView(LoginView):
    template_name = "clientes/login.html"
    redirect_authenticated_user = True


class UsuarioLogoutView(LogoutView):
    next_page = reverse_lazy("inicio")

class ReservaPedidoCreateView(LoginRequiredMixin, CreateView):
    model = Reserva_Pedido
    form_class = ReservaPedidoForm
    template_name = "clientes/reserva_form.html"
    success_url = reverse_lazy("mis_reservas")

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        form.instance.empresa_id = self.request.session.get("empresa_id")
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

def cancelar_reserva(request, pk):
    reserva = get_object_or_404(
        Reserva_Pedido,
        pk=pk,
        cliente=request.user
    )

    reserva.estado = "CANCELADO"
    reserva.save()

    messages.success(request, "Reserva cancelada.")
    return redirect("mis_reservas")

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
