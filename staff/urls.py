"""
URL configuration for chefquest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = "staff"

urlpatterns = [


    path("login-empresa/", views.login_empresa, name="login_empresa"),
    path("logout-empresa/", views.logout_empresa, name="logout_empresa"),


    path("productos/", views.ProductoListView.as_view(), name="producto_list"),
    path("productos/nuevo/", views.ProductoCreateView.as_view(), name="producto_create"),
    path("productos/<int:pk>/editar/", views.ProductoUpdateView.as_view(), name="producto_update"),
    path("productos/<int:pk>/eliminar/", views.ProductoDeleteView.as_view(), name="producto_delete"),


    path("reservas/", views.ReservasEmpresaListView.as_view(), name="lista_reservas_staff"),
    path("reservas/<int:pk>/confirmar/", views.confirmar_reserva, name="confirmar_reserva"),


    path("estadisticas/", views.EstadisticasView.as_view(), name="estadisticas"),
]
