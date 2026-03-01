# staff/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Empresa
from .utils import get_empresa_id_from_user

def empresa_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        empresa_id = request.session.get("empresa_id")
        if empresa_id and Empresa.objects.filter(pk=empresa_id, activo=True).exists():
            return view_func(request, *args, **kwargs)

        empresa_id_from_user = get_empresa_id_from_user(request.user)
        if empresa_id_from_user and Empresa.objects.filter(pk=empresa_id_from_user, activo=True).exists():
            request.session["empresa_id"] = empresa_id_from_user
            return view_func(request, *args, **kwargs)

        messages.error(request, "No tienes una empresa activa asociada a tu cuenta.")
        return redirect("inicio")
    return wrapper
