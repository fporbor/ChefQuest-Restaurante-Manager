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
from django.contrib import admin
from django.urls import path, include
from clientes.views import inicio, cambiar_tema
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Inicio público
    path("", inicio, name="inicio"),

    # Cambiar tema (cookie)
    path("tema/", cambiar_tema, name="cambiar_tema"),

    # Apps
    path("clientes/", include("clientes.urls")),
    path("staff/", include("staff.urls")),
path("accounts/", include("django.contrib.auth.urls")),
]
