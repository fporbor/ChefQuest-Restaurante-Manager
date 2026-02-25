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

urlpatterns = [


    path("registro/", views.UsuarioCreateView.as_view(), name="registro"),
    path("login/", views.UsuarioLoginView.as_view(), name="login"),
    path("logout/", views.UsuarioLogoutView.as_view(), name="logout"),
    path("", views.inicio, name="inicio"),
    path("reservas/", views.MisReservasListView.as_view(), name="mis_reservas"),
    path("reservas/nueva/", views.ReservaPedidoCreateView.as_view(), name="reserva_create"),
    path("reservas/<int:pk>/", views.ReservaDetailView.as_view(), name="reserva_detail"),
    path("reservas/<int:pk>/cancelar/", views.cancelar_reserva, name="cancelar_reserva"),
]
