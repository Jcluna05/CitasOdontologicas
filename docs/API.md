# API REST - Citas Odontológicas

Documentación de la API REST del sistema de gestión de citas odontológicas.

## Base URL

```
http://localhost:8000/api/
```

## Autenticación

La API soporta dos métodos de autenticación:

### 1. Token Authentication

```bash
# Obtener token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@consultorio.com", "password": "admin123"}'

# Respuesta
{
  "token": "abc123...",
  "user": {
    "id": 1,
    "email": "admin@consultorio.com",
    "first_name": "Admin",
    "last_name": "Sistema"
  }
}

# Usar token en requests
curl http://localhost:8000/api/patients/ \
  -H "Authorization: Token abc123..."
```

### 2. Session Authentication

Para uso desde el navegador con cookies de sesión (para testing con Browsable API).

## Endpoints

### Autenticación

#### POST `/api/auth/login/`

Login y obtención de token.

**Request Body:**
```json
{
  "email": "usuario@email.com",
  "password": "contraseña"
}
```

**Response:**
```json
{
  "token": "string",
  "user": {
    "id": 1,
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "role": "admin|reception|professional"
  }
}
```

#### POST `/api/auth/logout/`

Cerrar sesión e invalidar token.

#### GET `/api/auth/me/`

Obtener información del usuario actual.

---

### Pacientes

#### GET `/api/patients/`

Listar pacientes.

**Query Parameters:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| search | string | Buscar por nombre, teléfono o historia clínica |
| status | string | Filtrar por estado (active, inactive, blocked) |
| with_warnings | boolean | Solo pacientes con alertas |
| page | int | Número de página |

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/patients/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "medical_record_number": "HC-2024-0001",
      "full_name": "Juan Pérez",
      "phone": "999-111-222",
      "age": 35,
      "status": "active",
      "has_warnings": false,
      "no_show_count": 0
    }
  ]
}
```

#### POST `/api/patients/`

Crear paciente.

**Request Body:**
```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "999-111-222",
  "email": "juan@email.com",
  "birth_date": "1990-05-15",
  "has_anxiety": false,
  "has_allergies": true,
  "allergies_detail": "Alergia a penicilina"
}
```

#### GET `/api/patients/{id}/`

Obtener detalle de paciente.

#### PUT `/api/patients/{id}/`

Actualizar paciente.

#### DELETE `/api/patients/{id}/`

Eliminar paciente.

#### POST `/api/patients/{id}/register_no_show/`

Registrar inasistencia.

**Response:**
```json
{
  "message": "Inasistencia registrada.",
  "no_show_count": 1,
  "requires_advance_payment": false
}
```

#### GET `/api/patients/{id}/appointments/`

Obtener citas del paciente.

---

### Citas

#### GET `/api/appointments/`

Listar citas.

**Query Parameters:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| date | date | Filtrar por fecha exacta (YYYY-MM-DD) |
| date_from | date | Fecha desde |
| date_to | date | Fecha hasta |
| professional | int | ID del profesional |
| patient | int | ID del paciente |
| status | string | pending, confirmed, attended, cancelled, no_show |

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "patient": 1,
      "patient_name": "Juan Pérez",
      "professional": 1,
      "professional_name": "Dra. María Martínez",
      "procedure_type": 1,
      "procedure_name": "Evaluación",
      "procedure_color": "#3B82F6",
      "date": "2024-01-15",
      "start_time": "09:00",
      "end_time": "09:30",
      "status": "pending",
      "status_display": "Pendiente",
      "status_color": "warning"
    }
  ]
}
```

#### POST `/api/appointments/`

Crear cita.

**Request Body:**
```json
{
  "patient": 1,
  "professional": 1,
  "procedure_type": 1,
  "date": "2024-01-15",
  "start_time": "09:00",
  "notes": "Primera consulta"
}
```

> **Nota:** `end_time` se calcula automáticamente según la duración del procedimiento.

#### GET `/api/appointments/{id}/`

Obtener detalle de cita.

**Response incluye:**
- Datos completos del paciente y profesional
- Mensaje formateado para WhatsApp
- Estados de acción disponibles

#### PUT `/api/appointments/{id}/`

Actualizar cita.

#### DELETE `/api/appointments/{id}/`

Eliminar cita.

#### POST `/api/appointments/{id}/confirm/`

Confirmar cita.

**Response:**
```json
{
  "message": "Cita confirmada exitosamente.",
  "status": "confirmed"
}
```

#### POST `/api/appointments/{id}/cancel/`

Cancelar cita.

**Request Body:**
```json
{
  "reason": "Paciente solicitó cancelación"
}
```

#### POST `/api/appointments/{id}/attended/`

Marcar cita como atendida.

#### POST `/api/appointments/{id}/no_show/`

Marcar como no asistió (incrementa contador del paciente).

#### GET `/api/appointments/{id}/whatsapp_message/`

Obtener mensaje formateado para WhatsApp.

**Response:**
```json
{
  "message": "*CITA ODONTOLÓGICA*\n\n*Paciente:* Juan Pérez\n..."
}
```

#### GET `/api/appointments/today/`

Obtener citas de hoy.

#### GET `/api/appointments/upcoming/`

Obtener citas de los próximos 7 días.

---

### Procedimientos

#### GET `/api/procedures/`

Listar tipos de procedimientos.

**Query Parameters:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| is_active | boolean | Filtrar por estado |

**Response:**
```json
{
  "count": 6,
  "results": [
    {
      "id": 1,
      "name": "Evaluación",
      "description": "",
      "duration_minutes": 30,
      "color": "#3B82F6",
      "requires_confirmation": true,
      "is_active": true,
      "order": 1
    }
  ]
}
```

#### POST `/api/procedures/`

Crear procedimiento.

#### PUT `/api/procedures/{id}/`

Actualizar procedimiento.

#### DELETE `/api/procedures/{id}/`

Eliminar procedimiento.

---

### Disponibilidad

#### GET `/api/availability/`

Consultar slots disponibles.

**Query Parameters:**
| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| date | date | Sí | Fecha a consultar (YYYY-MM-DD) |
| professional | int | Sí | ID del profesional |
| duration | int | No | Duración en minutos (default: 30) |

**Response:**
```json
[
  {
    "start_time": "09:00",
    "end_time": "09:30",
    "formatted": "09:00 - 09:30"
  },
  {
    "start_time": "09:30",
    "end_time": "10:00",
    "formatted": "09:30 - 10:00"
  }
]
```

---

### Profesionales

#### GET `/api/professionals/`

Listar profesionales.

**Query Parameters:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| is_active | boolean | Filtrar por estado |

#### GET `/api/professionals/{id}/`

Detalle de profesional.

#### GET `/api/professionals/{id}/schedules/`

Obtener horarios del profesional.

---

### Dashboard / Estadísticas

#### GET `/api/dashboard/stats/`

Obtener estadísticas para el dashboard.

**Response:**
```json
{
  "today": {
    "total": 10,
    "pending": 3,
    "confirmed": 5,
    "attended": 2,
    "cancelled": 0,
    "no_show": 0
  },
  "week": {
    "total": 45,
    "cancelled_pct": 5.5,
    "no_show_pct": 2.2
  },
  "top_procedures": [
    {"procedure_type__name": "Evaluación", "count": 15},
    {"procedure_type__name": "Profilaxis", "count": 10}
  ],
  "top_no_shows": [
    {"id": 5, "first_name": "Pedro", "last_name": "García", "no_show_count": 3}
  ]
}
```

---

## Códigos de Estado

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Error de validación |
| 401 | Unauthorized - No autenticado |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

## Errores

**Formato de error:**
```json
{
  "detail": "Mensaje de error general",
  "field_name": ["Error específico del campo"]
}
```

**Ejemplo de error de validación:**
```json
{
  "start_time": ["El profesional ya tiene una cita de 09:00 a 09:30."],
  "patient": ["Este campo es requerido."]
}
```

## Paginación

Todas las listas usan paginación por defecto (20 items por página).

**Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/endpoint/?page=2",
  "previous": null,
  "results": []
}
```

## Filtros y Búsqueda

### Operadores de filtro

Los endpoints soportan:
- Filtros exactos: `?status=pending`
- Rangos de fecha: `?date_from=2024-01-01&date_to=2024-01-31`
- Búsqueda: `?search=juan`

### Ordenamiento

Algunos endpoints soportan ordenamiento:
```
?ordering=date
?ordering=-date  # Descendente
?ordering=date,start_time  # Múltiples campos
```

## Documentación Interactiva

- **Swagger UI:** `/api/docs/`
- **ReDoc:** `/api/redoc/`
- **OpenAPI Schema:** `/api/schema/`

## Ejemplos con cURL

### Listar citas de hoy
```bash
curl -X GET "http://localhost:8000/api/appointments/today/" \
  -H "Authorization: Token abc123..."
```

### Crear una cita
```bash
curl -X POST "http://localhost:8000/api/appointments/" \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "patient": 1,
    "professional": 1,
    "procedure_type": 1,
    "date": "2024-01-15",
    "start_time": "10:00"
  }'
```

### Confirmar una cita
```bash
curl -X POST "http://localhost:8000/api/appointments/1/confirm/" \
  -H "Authorization: Token abc123..."
```

### Consultar disponibilidad
```bash
curl -X GET "http://localhost:8000/api/availability/?date=2024-01-15&professional=1&duration=30" \
  -H "Authorization: Token abc123..."
```
