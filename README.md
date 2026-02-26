# ChefQuest: Restaurante Manager 

Sistema integral de gestión para restaurantes desarrollado con **Django** y **PostgreSQL**. Este proyecto utiliza **Docker** para garantizar un entorno de desarrollo idéntico para todo el equipo, cumpliendo con los requisitos de infraestructura y persistencia.

---

## Equipo y Roles
* **Responsable de Infraestructura y Documentación**: Álvaro Sibón Gonzalez
* **Responsable de Datos (ORM)**: Fran
* **Responsable de Usuarios y Flujo**: Ángel 

---

## Instalación y Despliegue rápido

Para levantar el proyecto sin necesidad de instalar Python o Postgres localmente, sigue estos pasos:

### 1. Levantar los contenedores
Este comando construye la imagen de la web a partir del `Dockerfile` y configura la base de datos PostgreSQL.
```bash
docker-compose up --build
```

### 2. Aplicar migracionesEs obligatorio ejecutar esto la primera vez para crear las tablas en PostgreSQL:

```bash
Bashdocker-compose exec web python manage.py migrate
```
### 3. Acceso al Panel de AdministraciónYa se ha configurado un superusuario para la gestión del sistema:
* **Username**: eladminguay
* **Email**: mangeldelaguilabarroso@gmail.com
* **Password**: eladmin123
* **Accede en**: http://localhost:8000/admin 

### Comandos útiles de Docker
Acción: Comando
* **Encender servicios**: docker-compose up
* **Apagar y liberar recursos**: docker-compose down
* **Ver errores (Logs)**: docker-compose logs -f web
* **Entrar al terminal del contenedor**: docker-compose exec web bash
* **Reconstruir tras cambios en requirements**: docker-compose up --build

### Detalles de Infraestructura (Puntos L, M, N, O)
Para cumplir con la rúbrica oficial, se han implementado los siguientes elementos técnicos:
* **Motor de Base de Datos**: Uso de PostgreSQL 15 (sustituyendo SQLite).
* **Persistencia**: Configuración de un volumen nombrado (postgres_data) para asegurar que los datos no se borren al reiniciar los contenedores.
* **Seguridad (Variables de Entorno)**: La SECRET_KEY y las credenciales de la base de datos se gestionan externamente mediante el archivo de configuración de Docker.
* **Aislamiento de Red**: Comunicación entre servicios mediante una red virtual interna (chefquest_network).

### Mapa de Trazabilidad
ID,Requisito,Ubicación / Evidencia
R-12,Dockerización Completa,Dockerfile y docker-compose.yml
R-12.2,Persistencia de datos,Volumen postgres_data en Docker
R-13,Gestión de dependencias,Archivo requirements.txt
R-14,Documentación técnica,Este archivo README.md