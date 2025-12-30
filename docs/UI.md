# Design System - Citas Odontológicas

Este documento define el sistema de diseño para la aplicación de gestión de citas odontológicas.

## Paleta de Colores

### Colores Principales

| Nombre | Hex | RGB | Uso |
|--------|-----|-----|-----|
| Primary | `#1D4ED8` | 29, 78, 216 | Acciones principales, enlaces, elementos destacados |
| Secondary | `#06B6D4` | 6, 182, 212 | Acciones secundarias, información |
| Success | `#16A34A` | 22, 163, 74 | Estados positivos, confirmaciones |
| Warning | `#F59E0B` | 245, 158, 11 | Alertas, advertencias |
| Danger | `#DC2626` | 220, 38, 38 | Errores, acciones destructivas |

### Colores Neutros

| Nombre | Hex | Uso |
|--------|-----|-----|
| Neutral-900 | `#0F172A` | Texto principal, sidebar |
| Neutral-700 | `#334155` | Texto secundario |
| Neutral-500 | `#64748B` | Texto deshabilitado |
| Neutral-100 | `#F1F5F9` | Fondos, separadores |
| Background | `#FFFFFF` | Fondo principal, cards |

### Estados de Cita

| Estado | Color | Clase CSS |
|--------|-------|-----------|
| Pendiente | Warning (`#F59E0B`) | `badge-pending`, `bg-warning` |
| Confirmada | Secondary (`#06B6D4`) | `badge-confirmed`, `bg-info` |
| Atendido | Success (`#16A34A`) | `badge-attended`, `bg-success` |
| Cancelado | Danger (`#DC2626`) | `badge-cancelled`, `bg-danger` |
| No asistió | Neutral-900 (`#0F172A`) | `badge-no-show`, `bg-dark` |

## Tipografía

### Fuente Principal

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Escalas

| Elemento | Tamaño | Peso |
|----------|--------|------|
| H1 | 1.5rem (24px) | 600 (Semibold) |
| H2 | 1.25rem (20px) | 600 (Semibold) |
| H3 | 1.125rem (18px) | 600 (Semibold) |
| Body | 1rem (16px) | 400 (Regular) |
| Small | 0.875rem (14px) | 400 (Regular) |
| Caption | 0.75rem (12px) | 400 (Regular) |

## Espaciado

Base: **8px**

| Nombre | Valor | Uso |
|--------|-------|-----|
| xs | 4px | Espaciado mínimo |
| sm | 8px | Espaciado pequeño |
| md | 16px | Espaciado medio |
| lg | 24px | Espaciado grande |
| xl | 32px | Espaciado extra grande |
| 2xl | 48px | Secciones principales |

## Componentes

### Cards

```html
<div class="card">
    <div class="card-header">
        <i class="bi bi-icon me-2"></i>Título
    </div>
    <div class="card-body">
        Contenido
    </div>
</div>
```

Estilos:
- Border radius: 0.75rem (12px)
- Box shadow: 0 1px 3px rgba(0, 0, 0, 0.1)
- Sin borde visible

### Badges

```html
<!-- Estados de cita -->
<span class="badge bg-warning">Pendiente</span>
<span class="badge bg-info">Confirmada</span>
<span class="badge bg-success">Atendido</span>
<span class="badge bg-danger">Cancelado</span>
<span class="badge bg-dark">No asistió</span>

<!-- Procedimientos (con color dinámico) -->
<span class="badge" style="background-color: #1D4ED8">Evaluación</span>
```

### Botones

```html
<!-- Primario -->
<button class="btn btn-primary">
    <i class="bi bi-plus-lg me-1"></i> Acción Principal
</button>

<!-- Secundario -->
<button class="btn btn-outline-primary">Acción Secundaria</button>

<!-- Peligro -->
<button class="btn btn-danger">Acción Destructiva</button>

<!-- Grupo de botones -->
<div class="btn-group btn-group-sm">
    <button class="btn btn-outline-secondary"><i class="bi bi-eye"></i></button>
    <button class="btn btn-outline-secondary"><i class="bi bi-pencil"></i></button>
</div>
```

### Tablas

```html
<div class="table-responsive">
    <table class="table table-hover mb-0">
        <thead>
            <tr>
                <th>Columna</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Dato</td>
            </tr>
        </tbody>
    </table>
</div>
```

Estilos del header:
- Font weight: 600
- Background: Neutral-100

### Formularios

```html
<div class="mb-3">
    <label class="form-label">Campo</label>
    <input type="text" class="form-control">
</div>

<div class="mb-3">
    <label class="form-label">Selección</label>
    <select class="form-select">
        <option>Opción</option>
    </select>
</div>

<div class="form-check">
    <input type="checkbox" class="form-check-input">
    <label class="form-check-label">Opción</label>
</div>
```

### Alertas

```html
<!-- Información -->
<div class="alert alert-info">
    <i class="bi bi-info-circle me-2"></i>
    Mensaje informativo
</div>

<!-- Éxito -->
<div class="alert alert-success alert-dismissible fade show">
    Operación exitosa
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>

<!-- Advertencia -->
<div class="alert alert-warning">
    <i class="bi bi-exclamation-triangle me-2"></i>
    Advertencia importante
</div>

<!-- Error -->
<div class="alert alert-danger">
    <i class="bi bi-x-circle me-2"></i>
    Error en la operación
</div>
```

### Sidebar

```html
<nav class="sidebar">
    <a class="logo-text" href="/">
        <i class="bi bi-heart-pulse"></i> OdontoCitas
    </a>

    <ul class="nav flex-column">
        <li class="nav-item">
            <a class="nav-link active" href="#">
                <i class="bi bi-speedometer2"></i> Dashboard
            </a>
        </li>
    </ul>
</nav>
```

Estilos:
- Background: Neutral-900
- Links: rgba(255, 255, 255, 0.7)
- Links hover/active: #fff con fondo rgba(255, 255, 255, 0.1)

## Iconografía

Usamos [Bootstrap Icons](https://icons.getbootstrap.com/).

### Iconos frecuentes

| Uso | Icono | Clase |
|-----|-------|-------|
| Dashboard | Velocímetro | `bi-speedometer2` |
| Calendario/Agenda | Calendario | `bi-calendar3` |
| Pacientes | Personas | `bi-people` |
| Cita | Evento | `bi-calendar-event` |
| Agregar | Plus | `bi-plus-lg` |
| Editar | Lápiz | `bi-pencil` |
| Ver | Ojo | `bi-eye` |
| Eliminar | Papelera | `bi-trash` |
| Confirmar | Check | `bi-check` |
| Cancelar | X | `bi-x-lg` |
| Configuración | Engranaje | `bi-gear` |
| Usuario | Persona | `bi-person` |
| Teléfono | Teléfono | `bi-telephone` |
| WhatsApp | WhatsApp | `bi-whatsapp` |
| Alerta | Triángulo | `bi-exclamation-triangle` |
| Reloj | Reloj | `bi-clock` |
| Búsqueda | Lupa | `bi-search` |

## Responsive

### Breakpoints (Bootstrap 5)

| Nombre | Mínimo | Máximo |
|--------|--------|--------|
| xs | 0 | 575px |
| sm | 576px | 767px |
| md | 768px | 991px |
| lg | 992px | 1199px |
| xl | 1200px | 1399px |
| xxl | 1400px | - |

### Consideraciones

- Sidebar colapsa en móviles (< md)
- Tablas usan `table-responsive` para scroll horizontal
- Cards en grid de 1-4 columnas según viewport
- Formularios de 1-2 columnas en móvil

## Animaciones

### Transiciones

```css
transition: all 0.2s ease-in-out;
```

Usadas en:
- Hover de botones
- Hover de links del sidebar
- Fade de alertas

## Accesibilidad

- Contraste mínimo WCAG AA (4.5:1 para texto normal)
- Focus visible en elementos interactivos
- Labels asociados a inputs
- Textos alternativos en iconos importantes
- Navegación por teclado funcional

## Ejemplos de Layouts

### Page Header

```html
<div class="page-header d-flex justify-content-between align-items-center">
    <div>
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb mb-1">
                <li class="breadcrumb-item"><a href="#">Inicio</a></li>
                <li class="breadcrumb-item active">Página</li>
            </ol>
        </nav>
        <h1>Título de Página</h1>
    </div>
    <div>
        <a href="#" class="btn btn-primary">
            <i class="bi bi-plus-lg me-1"></i> Acción
        </a>
    </div>
</div>
```

### Stats Cards

```html
<div class="row g-4 mb-4">
    <div class="col-md-3">
        <div class="card h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="text-muted mb-1">Título</h6>
                        <h2 class="mb-0">123</h2>
                    </div>
                    <div class="bg-primary bg-opacity-10 p-3 rounded">
                        <i class="bi bi-icon text-primary fs-4"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

### Empty State

```html
<div class="text-center py-5">
    <i class="bi bi-calendar-x text-muted" style="font-size: 3rem;"></i>
    <p class="text-muted mt-2">No hay datos disponibles</p>
    <a href="#" class="btn btn-primary">
        <i class="bi bi-plus-lg me-1"></i> Crear nuevo
    </a>
</div>
```
