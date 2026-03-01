from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied


class EmpresaEnSesionMixin(UserPassesTestMixin):
    """
    Verifica que haya una empresa activa en sesión.
    """

    def test_func(self):
        return self.request.session.get("empresa_id") is not None


class EmpresaStaffMixin:
    """
    El staff solo puede ver productos y reservas
    de la empresa que está en sesión.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        empresa_id = self.request.session.get("empresa_id")
        return qs.filter(empresa_id=empresa_id)


class ClientePropietarioMixin:
    """
    El cliente solo puede ver sus propias reservas/pedidos.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(cliente=self.request.user)

class UsuarioEmpresaRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        empresa_id = request.session.get("empresa_id")

        if not empresa_id:
            raise PermissionDenied("No hay empresa activa en sesión.")

        return super().dispatch(request, *args, **kwargs)