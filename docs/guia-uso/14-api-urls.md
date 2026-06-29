# 14 — API y URLs

Referencia técnica de rutas HTTP y JSON-RPC.

## Autenticación

Todas las rutas públicas validan:

```
station_id  → ID numérico estación
token       → access_token UUID (consteq timing-safe)
```

Token inválido → `404` (HTTP) o `{"error": "not_found"}` (JSON-RPC).

## Páginas HTML (GET)

| Ruta | Template | Uso |
|------|----------|-----|
| `/ticketmaton/kiosk/<station_id>/<token>` | kiosk_page | Kiosco cliente |
| `/ticketmaton/display/<station_id>/<token>` | display_page | Pantalla TV |
| `/ticketmaton/control/<station_id>/<token>` | control_page | Panel empleado |
| `/ticketmaton/<station_id>/<token>/logo` | binario imagen | Logo estación |

## JSON-RPC (POST)

Base: `/ticketmaton/<station_id>/<token>/<endpoint>`

Cuerpo estándar Odoo 19:

```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": { },
  "id": 1
}
```

### `config`

**Params:** ninguno

**Respuesta:** configuración pública kiosco/display

```json
{
  "id": 1,
  "name": "Tienda",
  "welcome_message": "Bienvenido",
  "queues": [
    {
      "id": 1,
      "name": "Atención",
      "button_label": "Atención",
      "button_color": "#2980b9",
      "button_icon": "fa-ticket"
    }
  ],
  "print_mode": "browser",
  "logo": "/ticketmaton/1/TOKEN/logo"
}
```

---

### `take_ticket`

**Params:**

| Param | Tipo | Requerido |
|-------|------|-----------|
| queue_id | int | sí |

**Respuesta OK:**

```json
{
  "ticket": { "id": 42, "number": "A042", "state": "waiting", ... },
  "print_data": { "header": "...", "number": "A042", "width_mm": 58 }
}
```

**Errores:**

| error | Significado |
|-------|-------------|
| not_found | Token/estación inválida |
| invalid_queue | Cola no existe o no pertenece a estación |
| create_failed | Numeración agotada u otro error |

---

### `display_state`

**Params:** ninguno

**Respuesta:**

```json
{
  "station_name": "Tienda",
  "queues": [
    {
      "id": 1,
      "name": "Atención",
      "current": "A042",
      "current_id": 42,
      "call_token": "2026-06-29 10:35:00",
      "active_calls": [...],
      "next": ["A043", "A044"]
    }
  ]
}
```

---

### `control_state`

**Params:** ninguno

**Respuesta:**

```json
{
  "station_name": "Tienda",
  "desks": [{ "id": 3, "name": "Mesa 1", "queue_ids": [] }],
  "queues": [
    {
      "id": 1,
      "waiting_total": 5,
      "next": ["A042"],
      "active_calls": [...]
    }
  ]
}
```

---

### `call_next`

**Params:**

| Param | Tipo | Requerido |
|-------|------|-----------|
| queue_id | int | sí |
| desk_id | int | no |

**Respuesta OK:**

```json
{ "ticket": { "number": "A042", "desk_name": "Mesa 1", "state": "calling" } }
```

**Errores:** `no_waiting`, `invalid_queue`, `not_found`

---

### `recall`

**Params:** `queue_id`, `desk_id` (opcional)

**Respuesta OK:** `{ "ticket": { ... } }`

**Errores:** `no_active`, `invalid_queue`

---

### `skip`

**Params:** `queue_id`, `desk_id` (opcional)

**Respuesta:**

```json
{
  "skipped": true,
  "ticket": { "number": "A043", ... }
}
```

Salta turno activo de la mesa (si hay) y llama siguiente.

---

### `bus_channel`

**Params:** ninguno

**Respuesta:**

```json
{ "channel": "ticketmaton#ec89da6b-6cbc-4d58-ad79-d68e3bc776b0" }
```

Suscripción en frontend:

```javascript
bus_service.addChannel(channel);
bus_service.subscribe("ticketmaton/ticket_calling", callback);
```

## Eventos bus

| Evento | Payload |
|--------|---------|
| ticketmaton/ticket_created | ticket.get_public_data() |
| ticketmaton/ticket_calling | ticket.get_public_data() |
| ticketmaton/ticket_recall | ticket.get_public_data() |
| ticketmaton/ticket_done | ticket.get_public_data() |
| ticketmaton/ticket_skipped | ticket.get_public_data() |
| ticketmaton/ticket_cancelled | ticket.get_public_data() |

## Modelos Odoo (backend)

| Modelo | _name |
|--------|-------|
| Estación | ticketmaton.station |
| Cola | ticketmaton.queue |
| Mesa | ticketmaton.desk |
| Ticket | ticketmaton.ticket |

## URLs computadas (estación)

Generadas en `kiosk_url`, `display_url`, `control_url`:

```
{base_url}/ticketmaton/kiosk/{id}/{access_token}
{base_url}/ticketmaton/display/{id}/{access_token}
{base_url}/ticketmaton/control/{id}/{access_token}
```

`base_url` = `web.base.url` de Odoo.

## Ejemplo integración externa

Sacar turno desde script Python:

```python
import requests

url = "http://localhost:8069/ticketmaton/1/TOKEN/take_ticket"
payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {"queue_id": 1},
    "id": 1,
}
r = requests.post(url, json=payload)
data = r.json()["result"]
print(data["ticket"]["number"])  # A042
```

## Seguridad

- Token en URL = capacidad de sacar y llamar turnos
- No exponer panel en internet sin mitigación adicional
- HTTPS recomendado en producción
- `auth="public"` + `sudo()` en controladores — diseño intencional para kioscos sin login
