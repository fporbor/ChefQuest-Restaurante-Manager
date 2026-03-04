# clientes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, get_user_model
from django.db import transaction
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from .models import Usuario, Usuario_Perfil, Reserva_Pedido
from .forms import UsuarioRegistroForm, UsuarioPerfilForm, ReservaPedidoForm, LoginEmpresaForm
from staff.models import Producto, Empresa
from staff.mixins import ClientePropietarioMixin
from staff.forms import EmpresaRegistroForm

User = get_user_model()


def inicio(request):
    # Evitar N+1: traer relaciones necesarias con select_related/prefetch_related
    productos_activos = Producto.objects.filter(activo=True).select_related(
        "categoria__cupon", "empresa"
    )

    carta_del_dia_qs = productos_activos.filter(producto_del_dia=True)
    carta_del_dia = carta_del_dia_qs if carta_del_dia_qs.exists() else None

    productos = []
    for p in productos_activos:
        descuento = 0
        if getattr(p, "categoria", None) and getattr(p.categoria, "cupon", None):
            descuento = p.categoria.cupon.descuento or 0
        precio_final = round(p.precio * (100 - descuento) / 100, 2)
        productos.append({
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "precio": p.precio,
            "precio_descuento": precio_final,
            "categoria": p.categoria.nombre if p.categoria else "Sin categoría",
            "empresa": p.empresa.nombre_comercial if p.empresa else "Sin empresa",
        })

    return render(request, "clientes/inicio.html", {
        "productos": productos,
        "carta_del_dia": carta_del_dia,
    })


class UsuarioCreateView(CreateView):
    model = User
    form_class = UsuarioRegistroForm
    template_name = "registration/registro.html"
    success_url = reverse_lazy("clientes:inicio")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["perfil_form"] = UsuarioPerfilForm(self.request.POST or None)
        try:
            context["empresa_form"] = EmpresaRegistroForm(self.request.POST or None)
        except Exception:
            context["empresa_form"] = None
        return context

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        perfil_form = context["perfil_form"]
        empresa_form = context.get("empresa_form")

        if not perfil_form.is_valid():
            for field, errors in perfil_form.errors.items():
                for err in errors:
                    form.add_error(None, f"Perfil {field}: {err}")
            return self.form_invalid(form)

        es_empresa = form.cleaned_data.get("es_empresa")
        nombre_empresa = form.cleaned_data.get("nombre_empresa")
        post = self.request.POST

        # Validación empresa
        empresa_form_to_use = None
        if es_empresa:
            if empresa_form is not None:
                empresa_form_to_use = EmpresaRegistroForm(self.request.POST)
                if not empresa_form_to_use.is_valid():
                    for field, errors in empresa_form_to_use.errors.items():
                        for err in errors:
                            form.add_error(None, f"Empresa {field}: {err}")
                    return self.form_invalid(form)
            else:
                if not nombre_empresa:
                    form.add_error(None, "Si te registras como empresa debes indicar el nombre de la empresa.")
                    return self.form_invalid(form)

        # Crear usuario
        usuario = form.save()

        # Crear perfil
        perfil, created = Usuario_Perfil.objects.get_or_create(usuario=usuario)
        perfil_obj = perfil_form.save(commit=False)
        perfil.preferencias_de_comunicacion = getattr(perfil_obj, "preferencias_de_comunicacion", perfil.preferencias_de_comunicacion)
        perfil.direccion = getattr(perfil_obj, "direccion", perfil.direccion)
        perfil.observacion = getattr(perfil_obj, "observacion", perfil.observacion)
        perfil.save()

        # Crear empresa y asociarla al usuario
        if es_empresa:
            if empresa_form_to_use and empresa_form_to_use.is_valid():
                empresa = empresa_form_to_use.save()
            else:
                empresa = Empresa.objects.create(
                    nombre_comercial=nombre_empresa,
                    contacto=usuario.email,
                    codigo=form._generar_codigo_unico()
                )

            usuario.empresa = empresa
            usuario.save()

        # Asignar grupos
        try:
            if es_empresa:
                grupo, _ = Group.objects.get_or_create(name="Empresas")
                usuario.groups.add(grupo)
                usuario.is_staff = True
            else:
                grupo, _ = Group.objects.get_or_create(name="Usuarios")
                usuario.groups.add(grupo)
        except Exception:
            pass

        usuario.save()

        login(self.request, usuario)
        return redirect(self.success_url)


class UsuarioLogoutView(LogoutView):
    next_page = reverse_lazy("clientes:inicio")


class ReservaPedidoCreateView(LoginRequiredMixin, CreateView):
    model = Reserva_Pedido
    form_class = ReservaPedidoForm
    template_name = "clientes/reserva_form.html"
    success_url = reverse_lazy("clientes:mis_reservas")

    SESSION_KEY = "reserva_en_construccion"

    def get_initial(self):
        initial = super().get_initial()
        datos = self.request.session.get(self.SESSION_KEY)
        if datos:
            initial.update(datos)
        return initial

    def form_invalid(self, form):
        datos = self.request.POST.dict()
        datos.pop("csrfmiddlewaretoken", None)
        datos["productos"] = self.request.POST.getlist("productos")
        self.request.session[self.SESSION_KEY] = datos
        messages.warning(self.request, "Tu reserva se ha guardado temporalmente en sesión.")
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        # Si el modelo Reserva_Pedido no tiene campo empresa_id, no asignamos empresa aquí.
        # La pertenencia a empresa se determina por cliente.perfil.empresa o por productos al confirmar.
        form.instance.estado = "PENDIENTE"
        response = super().form_valid(form)
        if self.SESSION_KEY in self.request.session:
            del self.request.session[self.SESSION_KEY]
        messages.success(self.request, "Reserva creada correctamente.")
        return response


class ReservaPedidoUpdateView(LoginRequiredMixin, ClientePropietarioMixin, UpdateView):
    model = Reserva_Pedido
    form_class = ReservaPedidoForm
    template_name = "clientes/reserva_form.html"
    success_url = reverse_lazy("clientes:mis_reservas")

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        return super().form_valid(form)


class MisReservasListView(LoginRequiredMixin, ListView):
    model = Reserva_Pedido
    template_name = "clientes/mis_reservas.html"
    context_object_name = "reservas"

    def get_queryset(self):
        return (
            Reserva_Pedido.objects
            .filter(cliente=self.request.user)
            .select_related("cliente")
            .prefetch_related("productos")
        )


class ReservaDetailView(LoginRequiredMixin, ClientePropietarioMixin, DetailView):
    model = Reserva_Pedido
    template_name = "clientes/reserva_detail.html"

    def get_queryset(self):
        qs = super().get_queryset().filter(cliente=self.request.user)
        # Reserva_Pedido no tiene FK directa a empresa; evitar select_related("empresa")
        return qs.select_related("cliente").prefetch_related("productos")


@login_required
def cancelar_reserva(request, pk):
    reserva = get_object_or_404(Reserva_Pedido, pk=pk, cliente=request.user)
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
    tema = request.GET.get("tema", "claro")
    response = redirect("inicio")
    response.set_cookie("tema", tema, max_age=60 * 60 * 24 * 30)
    return response


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginEmpresaForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        form_class = self.get_form_class()
        # pasar request solo si el form lo soporta
        try:
            if isinstance(form_class, type) and issubclass(form_class, LoginEmpresaForm):
                kwargs['request'] = self.request
                if self.request.method == 'POST':
                    post = self.request.POST.copy()
                    # normalizar checkbox
                    post['es_empresa'] = 'True' if post.get('es_empresa') in ['on', 'true', '1'] else ''
                    kwargs['data'] = post
        except TypeError:
            pass
        return kwargs

    def form_valid(self, form):
        user = getattr(form, 'user', None)
        if not user:
            return self.form_invalid(form)

        login(self.request, user)

        # si autenticado como empresa, guardar empresa_id en sesión (opcional)
        if getattr(form, '_auth_via_codigo', False):
            # buscar empresa asociada por email o por código
            codigo = form.cleaned_data.get('codigo_empresa')
            empresa = None
            if codigo:
                empresa = Empresa.objects.filter(codigo=codigo).first()
            if not empresa:
                # intentar por email del usuario
                empresa = Empresa.objects.filter(contacto=user.email, activo=True).first()
            if empresa:
                self.request.session['empresa_id'] = empresa.id

        return redirect(self.get_success_url())

    def get_success_url(self):
        user = self.request.user
        if Empresa.objects.filter(contacto=user.email, activo=True).exists():
            return reverse_lazy("staff:producto_list")
        return reverse_lazy("inicio")
