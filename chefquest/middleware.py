import time

class SimpleLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Código que se ejecuta ANTES de que la vista procese la petición
        print(f"--- [LOG]: Nueva petición recibida: {request.path} ---")
        
        response = self.get_response(request)
        
        # 2. Código que se ejecuta DESPUÉS de que la vista devuelve la respuesta
        print(f"--- [LOG]: Petición procesada: {request.path} ---")
        return response