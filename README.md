# Sistema de Gestión de Citas Odontológicas

Sistema web completo para la gestión de citas en consultorios odontológicos, desarrollado con Django 5.x y Django REST Framework.

## Características

### MVP Implementado
- ✅ Gestión de consultorio (configuración, horarios)
- ✅ Registro y gestión de pacientes
- ✅ Agenda de citas con estados (Pendiente, Confirmada, Atendido, Cancelado, No asistió)
- ✅ Catálogo de procedimientos con duraciones configurables
- ✅ Control de inasistencias (reglas automáticas)
- ✅ Recordatorios y notificaciones (mock para desarrollo)
- ✅ Generación de mensaje para WhatsApp
- ✅ Historial de cambios de estado (auditoría)

### Características Innovadoras
- ✅ Motor de disponibilidad inteligente
- ✅ Triage rápido del paciente (alertas visuales)
- ✅ Dashboard con estadísticas (KPI)
- ✅ Plantillas de mensajes personalizables
- ✅ Historial de auditoría en citas

### Roles y Permisos
- **Administrador**: Acceso completo
- **Recepción**: CRUD pacientes/citas, ver configuración
- **Profesional**: Ver su agenda, marcar atendido, ver pacientes

## Stack Tecnológico

- **Backend**: Django 5.x, Django REST Framework
- **Base de datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **APIs**: REST API documentada con Swagger/OpenAPI

## Instalación

### Prerrequisitos
- Python 3.11+
- pip
- virtualenv (recomendado)

### Pasos

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd CitasOdontologicas
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env según sea necesario
```

5. **Crear y ejecutar migraciones**
```bash
python manage.py makemigrations accounts clinic patients appointments notifications
python manage.py migrate
```

6. **Crear datos iniciales**
```bash
# Solo datos base (procedimientos, plantillas, etc.)
python manage.py setup_initial_data

# Con datos demo (pacientes, profesionales, citas de ejemplo)
python manage.py setup_initial_data --with-demo
```

7. **Crear superusuario (si no usaste --with-demo)**
```bash
python manage.py createsuperuser
```

8. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

9. **Acceder a la aplicación**
- Web: http://localhost:8000
- Admin: http://localhost:8000/admin
- API Docs: http://localhost:8000/api/docs/

### Credenciales Demo

Si ejecutaste `setup_initial_data --with-demo`:

| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | admin@consultorio.com | admin123 |
| Profesional | dra.martinez@consultorio.com | doctor123 |
| Profesional | dr.rodriguez@consultorio.com | doctor123 |
| Recepción | recepcion@consultorio.com | recepcion123 |

## Estructura del Proyecto

```
CitasOdontologicas/
├── apps/
│   ├── accounts/      # Usuarios, autenticación, roles
│   ├── clinic/        # Consultorio, profesionales, horarios
│   ├── patients/      # Pacientes, triage, eventos
│   ├── appointments/  # Citas, procedimientos, agenda
│   └── notifications/ # Recordatorios, logs de notificaciones
├── config/            # Configuración Django
├── templates/         # Templates HTML
├── static/            # Archivos estáticos
├── docs/              # Documentación
└── manage.py
```

## Comandos Útiles

### Enviar recordatorios
```bash
# Ver qué citas recibirían recordatorio (sin enviar)
python manage.py send_reminders --dry-run

# Enviar recordatorios
python manage.py send_reminders

# Recordatorios 48 horas antes
python manage.py send_reminders --hours=48
```

### Cron job para recordatorios (Linux)
```bash
# Agregar a crontab -e
0 8 * * * cd /path/to/project && /path/to/venv/bin/python manage.py send_reminders
```

## API REST

La API está documentada y accesible en:
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- Schema: `/api/schema/`

### Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /api/auth/login/ | Login |
| GET | /api/patients/ | Listar pacientes |
| POST | /api/patients/ | Crear paciente |
| GET | /api/appointments/ | Listar citas |
| POST | /api/appointments/ | Crear cita |
| GET | /api/availability/ | Consultar disponibilidad |
| GET | /api/procedures/ | Listar procedimientos |

Ver [docs/API.md](docs/API.md) para documentación completa.

## Configuración para Producción

### PostgreSQL
```bash
# En .env
DATABASE_URL=postgres://user:password@localhost:5432/citas_db
```

### Variables de entorno importantes
```bash
DEBUG=False
SECRET_KEY=<clave-segura-generada>
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
```

### Archivos estáticos
```bash
python manage.py collectstatic
```

## Design System

Ver [docs/UI.md](docs/UI.md) para la documentación completa del sistema de diseño.

### Paleta de colores
- Primary: `#1D4ED8` (azul confianza)
- Secondary: `#06B6D4` (cian)
- Success: `#16A34A`
- Warning: `#F59E0B`
- Danger: `#DC2626`

### Estados de cita
- Pendiente: Warning (amarillo)
- Confirmada: Secondary (cian)
- Atendido: Success (verde)
- Cancelado: Danger (rojo)
- No asistió: Dark (gris oscuro)

## Contribuir

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.
