# Sistema de Gestion de Salones de Eventos (Proyecto Salon)

Plataforma integral para la administracion operativa de salones de eventos y red de vinculacion laboral para personal de servicio (meseros y capitanes).

---

## 1. Descripcion General y Objetivos

Proyecto Salon es una aplicacion de escritorio disenada para conectar y resolver las necesidades operativas de cuatro perfiles de usuario:

- **Patron / Administrador del Salon:** Control de disponibilidad de fechas, configuracion de croquis interactivos con distribucion de mesas y servicios, administracion de inventario periodico, calculo de costos de reposicion por faltantes/danos y monitoreo de estadisticas de eventos.
- **Capitan / Coordinador Operativo:** Recepcion de eventos programados, calculo automatico del personal requerido con base en el aforo, asignacion de zonas y mesas por mesero sobre el croquis, y evaluacion del servicio tras cada evento.
- **Mesero (Enfoque de Desarrollo y Equidad Laboral):** Modulo orientado a dignificar el trabajo del personal de servicio. Permite consultar asignaciones en croquis, registrar opiniones y propinas recibidas por evento, y sentar las bases para una bolsa de trabajo transparente (con sueldos y propinas estimadas claras) y la construccion de un historial laboral verificable basado en reputacion.
- **Usuario / Cliente General:** Modulo proyectado para la busqueda y comparacion de salones por zona, capacidad, precios estimados y calificaciones promedio.

---

## 2. Estructura del Repositorio

El proyecto cuenta con una arquitectura modular por capas (dominio, datos y presentacion):

```text
proyecto-salon/
|-- main.py                     # Punto de entrada de la aplicacion
|-- constantes.py               # Constantes de configuracion, interfaz y rutas
|-- vistas.py                   # Modulo de compatibilidad para importacion de vistas
|-- salon.py                    # Prototipo inicial monolitico (respaldo de diseno)
|-- salon.db                    # Base de datos relacional SQLite3
|
|-- entidades/                  # Modelos de dominio y estructuras de datos
|   |-- __init__.py
|   `-- modelos.py              # Definicion de clases (Salon, Mesero, Evento, Mesa, etc.)
|
|-- datos/                      # Capa de persistencia y acceso a datos
|   |-- __init__.py
|   |-- base_datos.py           # Controlador SQLite3, migraciones y consultas
|   `-- gestor_archivos.py      # Interfaz de persistencia (SQLite, JSON y CSV)
|
|-- pantallas/                  # Capa de presentacion (interfaz grafica Tkinter)
|   |-- __init__.py
|   |-- app.py                  # Ventana principal y control de navegacion
|   |-- base.py                 # Clase base para frames de la interfaz
|   |-- lazy.py                 # Carga diferida de vistas para evitar dependencias circulares
|   |-- login.py                # Selector de perfil/rol de acceso
|   |-- menus.py                # Menus principales por rol (Patron, Capitan, Mesero)
|   |-- patron.py               # Vistas del Patron (reservaciones, calendario, eventos)
|   |-- perfil_salon.py         # Configuracion de datos generales y tarifas del salon
|   |-- dashboard_patron.py     # Panel analitico del patron (metricas y graficos)
|   |-- capitan.py              # Vistas del Capitan (organizacion y calculo de personal)
|   |-- mesero.py               # Vistas del Mesero (consulta de mesas y comentarios)
|   |-- croquis.py              # Canvas interactivo para distribucion de mesas y servicios
|   `-- inventario.py           # Control de inventario, bajas y costos de reposicion
|
|-- exports/                    # Reportes y exportaciones en formato CSV
|   |-- eventos.csv
|   `-- organizaciones.csv
|
|-- inventarios/                # Registros historicos de cortes de inventario
|   |-- inventario_2026-06-04_17-39-39.csv
|   `-- inventario_2026-06-04_17-54-19.csv
|
|-- eventos.json                # Archivos JSON utilizados para intercambio de datos
|-- organizacion.json
|-- inventario.json
|-- Plan construccion proyecto.txt # Documento de seguimiento de requerimientos
`-- README.md                   # Documentacion tecnica del repositorio
```

---

## 3. Estado Actual de Desarrollo

El desarrollo se encuentra estructurado en fases. A continuacion se detalla el estado funcional de cada componente:

### Modulos Completados
- **Base de Datos SQLite3 (`salon.db`):** Esquema relacional implementado para salones, eventos, mesas, organizaciones, inventarios, meseros, ofertas de trabajo, postulaciones y comentarios.
- **Panel Patron:**
  - Creacion y edicion de reservaciones con croquis de distribucion (mesas regulares, mesa principal, servicios: cocina, barra, pastel, dulces, pantalla, fotos y animador).
  - Calendario semestral con bloqueo de fechas ocupadas y navegacion sincronizada.
  - Perfil del salon (datos de contacto, zona, tarifas base y logo).
  - Gestion de inventario con calculo de reposicion y comparacion de mermas entre cortes.
  - Dashboard de estadisticas con metricas de ocupacion, ingresos y percepcion general.
- **Panel Capitan:**
  - Deteccion de eventos pendientes y asignacion de mesas a meseros con codigo de colores.
  - Algoritmo de sugerencia de cantidad de meseros segun numero de mesas.
  - Herramienta de comparacion entre eventos para analisis de aforo.
- **Panel Mesero (Fase Base):**
  - Consulta de mesas y zonas asignadas por evento.
  - Registro de comentarios, evaluacion del trato recibido y reporte de propinas.

### Modulos en Progreso
- **Perfil Profesional del Mesero:** Captura de habilidades, zonas de preferencia y evaluacion inicial para calculo de reputacion.
- **Bolsa de Trabajo y Ofertas:** Publicacion de vacantes por fecha/salon con sueldo y propina estimada, postulacion directa de meseros y aceptacion por parte del capitan.

### Modulos Planificados
- **Analizador de Sentimientos:** Procesamiento de comentarios y retroalimentacion para generar alertas y recomendaciones sin seccionar o senalar individuos.
- **Catalogo Publico para Usuarios:** Consulta de salones disponibles por zona y comparativa de cotizaciones.
- **Autenticacion Centralizada y Migracion Web:** Implementacion de sesiones de usuario y transicion a arquitectura cliente-servidor / web.

---

## 4. Requisitos y Ejecucion

### Requisitos del Sistema
- Python 3.10 o superior.
- Soporte para Tkinter (incluido en las instalaciones estandar de Python).

### Dependencias
Instalar los paquetes requeridos mediante pip:

```bash
pip install tkcalendar
```

### Ejecutar la Aplicacion
Para iniciar el sistema con la estructura modular actual:

```bash
python main.py
```

*Nota: El archivo `salon.py` corresponde a la version previa monolítica y se conserva unicamente como referencia de arquitectura.*

---

## 5. Mantenimiento y Contacto

Proyecto desarrollado y mantenido por **Hugo** ([TheShock25](https://github.com/TheShock25)).