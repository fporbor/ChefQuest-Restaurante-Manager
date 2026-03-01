
# staff/utils.py
from typing import Optional

def get_empresa_id_from_user(user) -> Optional[int]:
    """
    Devuelve el id de la empresa asociada al usuario (FK directa user.empresa) o None.
    Prioriza siempre user.empresa.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return None
    empresa = getattr(user, "empresa", None)
    return getattr(empresa, "id", None) if empresa else None
