# 10 — Tickets en backend Odoo

Gestión desde **Ticketmaton → Panel** (lista/kanban de tickets).

## Estados del ticket

| Estado | Código | Significado |
|--------|--------|-------------|
| En espera | `waiting` | Sacado en kiosco, no llamado |
| Llamando | `calling` | Llamado en pantalla |
| Atendiendo | `serving` | En mostrador (opcional) |
| Finalizado | `done` | Atención completada |
| Saltado | `skipped` | No se presentó / descartado |
| Cancelado | `cancelled` | Anulado manualmente |

## Campos del ticket

| Campo | Descripción |
|-------|-------------|
| Número | `number_display` (A042, 001…) |
| Cola | Cola origen |
| Estación | Estación |
| Mesa | Mostrador asignado al llamar |
| Fecha creación | Momento en kiosco |
| Fecha llamada | Momento SIGUIENTE |
| Fecha atención | Momento action_serve |
| Fecha fin | Momento done/skip/cancel |

## Vistas

### Lista / Kanban (Panel)

Filtros típicos:
- En espera
- Activos (calling/serving)
- Hoy

Tarjetas kanban por estado con botones rápidos **Llamar** y **Finalizar**.

### Formulario ticket

Botones según estado:

| Estado | Botones disponibles |
|--------|---------------------|
| waiting | Llamar, Saltar, Cancelar |
| calling | Atender, Rellamar, Finalizar, Saltar |
| serving | Finalizar, Rellamar, Saltar |

## Acciones manuales

### Llamar (`action_call`)

Pasa ticket a `calling`. Útil si el panel web no está disponible.

### Atender (`action_serve`)

Pasa a `serving` (intermedio opcional).

### Finalizar (`action_mark_done`)

Pasa a `done`. Cierra el turno.

### Rellamar (`action_recall`)

Actualiza `call_date` → overlay en pantalla TV.

### Saltar (`action_skip`)

Marca `skipped`. Cliente no atendido.

### Cancelar (`action_cancel`)

Anula ticket (`cancelled`).

## Gestión desde cola

**Ticketmaton → Colas → [cola]**

Botones en formulario cola:
- **Siguiente** → `action_call_next()` (igual que panel web)
- **Rellamar** → `action_recall_current()`
- **Reset contador** → reinicia numeración

## Ejemplo: supervisión desde oficina

```
1. Jefe abre Ticketmaton → Panel
2. Filtro "En espera" → ve cola acumulada
3. Si hay problema en mostrador, puede Llamar/Finalizar manualmente
4. Historial del día en lista con filtro fecha
```

## Ejemplo: cierre de turno atascado

```
Situación: pantalla muestra A040 pero cliente ya fue atendido
1. Buscar ticket A040 en Panel
2. Finalizar (o ya está done)
3. Mostrador pulsa SIGUIENTE para A041
```

## Notificaciones bus

Cada cambio de estado dispara evento en canal `ticketmaton#<token>`:

| Evento | Cuándo |
|--------|--------|
| ticket_created | Nuevo turno kiosco |
| ticket_calling | Llamado |
| ticket_recall | Rellamada |
| ticket_done | Finalizado |
| ticket_skipped | Saltado |
| ticket_cancelled | Cancelado |

Pantallas web escuchan para refresco rápido.

## Permisos

- **Usuario Ticketmaton:** ver y operar tickets
- **Administrador:** + configuración estaciones/col

## Consultas útiles (modo desarrollador)

Desde shell Odoo o filtros dominio:

```
# Todos en espera hoy
[('state','=','waiting'), ('create_date','>=', context_today)]

# Tickets de una estación
[('station_id','=', 1)]

# Por mesa
[('desk_id','=', 3)]
```
