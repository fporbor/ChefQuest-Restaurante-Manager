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
### Extras opcionales:
1. Modo “carta del día” (productos destacados configurables por staff).
2. Cupones simples (descuento fijo/porcentaje) aplicados en pedidos.
3. Sistema de aforo (bloquear reservas si se supera capacidad por franja horaria).

### Workflow seguido (Flujo de Trabajo)
Para garantizar la integridad del proyecto ChefQuest, se ha seguido un flujo de trabajo colaborativo basado en el modelo Git Flow, permitiendo el desarrollo paralelo de infraestructura y lógica de negocio.

* **Gestión de ramas e integración**
El proyecto se ha estructurado en ramas dedicadas para separar responsabilidades y evitar conflictos:

main: Rama principal que contiene la versión estable y desplegable.

infraestructura-docker: Rama dedicada a la configuración del entorno, Dockerización y base de datos (PostgreSQL).

rama-angel: Rama enfocada en la lógica de negocio, desarrollo de views, formularios y modelos.

Integración: Cada rama funcional se ha fusionado en main mediante git merge una vez validadas las tareas, asegurando que los cambios de infraestructura y los de lógica de aplicación convivieran sin errores.

* **Gestión de tareas (Issues)**
El trabajo se ha repartido mediante una división clara de competencias:

Se ha utilizado una metodología de trabajo por áreas: mientras el equipo de infraestructura preparaba el contenedor y la persistencia de datos, el equipo de desarrollo trabajaba en las funcionalidades del restaurante (views y forms).

Esto permitió avanzar en paralelo, minimizando los tiempos de espera y maximizando la eficiencia.

* **Revisión de código**
Se ha llevado a cabo una revisión cruzada (cross-review) antes de realizar los merges:

Se ha verificado que las vistas desarrolladas en rama-angel funcionaran correctamente sobre la base de datos configurada en infraestructura-docker.

Antes de integrar cualquier rama en main, se ha realizado un despliegue local completo utilizando docker compose up --build para asegurar que el entorno integrado fuera funcional.

* **Resolución de conflictos**
Dada la separación de ramas (Infraestructura vs. Lógica), los conflictos fueron mínimos:

Estos se resolvieron mediante la sincronización proactiva con main (git fetch y git merge), analizando los cambios en los archivos de configuración y modelos de Django para garantizar la compatibilidad total.