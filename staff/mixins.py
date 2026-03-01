# staff/mixins.py
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin
from .utils import get_empresa_id_from_user

class EmpresaEnSesionMixin:
    """
    Asegura que haya una empresa activa en sesión; si no, intenta obtenerla desde user.empresa.
    Fija request.session['empresa_id'] cuando la encuentra.
    """
    def dispatch(self, request, *args, **kwargs):
        empresa_id = request.session.get("empresa_id") or get_empresa_id_from_user(request.user)
        if not empresa_id:
            raise PermissionDenied("No hay empresa activa en sesión.")
        request.session["empresa_id"] = empresa_id
        return super().dispatch(request, *args, **kwargs)


class EmpresaStaffMixin:
    """
    Restringe el queryset a la empresa activa en sesión.
    Úsalo en CBV que llamen a super().get_queryset().
    """
    def get_queryset(self):
        qs = super().get_queryset()
        empresa_id = self.request.session.get("empresa_id") or get_empresa_id_from_user(self.request.user)
        if not empresa_id:
            raise PermissionDenied("No hay empresa activa en sesión.")
        return qs.filter(empresa_id=empresa_id)


class ClientePropietarioMixin:
    """
    Restringe el queryset a las instancias cuyo campo 'cliente' sea el usuario actual.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(cliente=self.request.user)


class UsuarioEmpresaRequiredMixin:
    """
    Comprueba que exista una empresa activa en sesión y que el usuario pertenezca a ella
    (comparando user.empresa con la empresa en sesión).
    """
    def dispatch(self, request, *args, **kwargs):
        empresa_id = request.session.get("empresa_id") or get_empresa_id_from_user(request.user)
        if not empresa_id:
            raise PermissionDenied("No hay empresa activa en sesión.")

        user_empresa = getattr(request.user, "empresa", None)
        if user_empresa and int(user_empresa.id) != int(empresa_id):
            raise PermissionDenied("No tienes permisos sobre la empresa activa.")

        # Si user.empresa es None, permitimos continuar solo si la sesión tiene empresa_id
        # (esto cubre casos donde la empresa se fijó en sesión tras el registro)
        return super().dispatch(request, *args, **kwargs)

