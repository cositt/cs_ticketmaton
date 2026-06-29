# 07 — Pantalla pública (TV)

URL: `/ticketmaton/display/<station_id>/<token>`

Dispositivo: TV o monitor en sala de espera. Muestra turnos actuales y avisa con overlay al llamar.

## Layout

```
┌──────────────────────────────────────────────────┐
│              TIENDA MÁLAGA                        │
├──────────────────┬───────────────────────────────┤
│  TURNO ACTUAL    │  SIGUIENTES                   │
│                  │                               │
│     A042         │  A043  A044  A045             │
│  (cola Atención) │                               │
└──────────────────┴───────────────────────────────┘

        [ OVERLAY al llamar ]
        ┌─────────────────────────┐
        │  Pase a mostrador         │
        │       A042                │
        │      Mesa 1               │
        └─────────────────────────┘
```

## Actualización en tiempo real

1. **Polling:** cada ~2s llama `display_state`
2. **Bus Odoo:** canal `ticketmaton#<access_token>` para eventos instantáneos

Eventos que disparan overlay:
- Nuevo turno llamado (`current_id` cambia)
- Rellamada (`call_token` cambia sin cambiar `current_id`)

## Campos configurables (estación)

| Campo | Uso en pantalla | Ejemplo |
|-------|-----------------|---------|
| display_now_label | Etiqueta turno actual | Turno actual |
| display_next_label | Etiqueta siguientes | Siguientes |
| display_call_prefix | Texto overlay llamada | Pase a mostrador |
| display_bg_color | Fondo | #0d1b2a |
| display_text_color | Texto principal | #ffffff |
| display_accent_color | Acentos / overlay | #e63946 |
| display_font_size | Tamaño número grande | 120 (px) |

### Ejemplo personalización

```
display_now_label:      "Ahora atiende"
display_next_label:     "En espera"
display_call_prefix:    "Diríjase a"
display_bg_color:       #1a1a2e
display_accent_color:   #ff6b6b
display_font_size:      150
```

## Estado por cola (`display_state`)

Cada cola activa devuelve:

```json
{
  "id": 1,
  "name": "Atención",
  "color": "#3498db",
  "current": "A042",
  "current_id": 42,
  "call_token": "2026-06-29 10:35:00",
  "active_calls": [
    {
      "number": "A042",
      "desk_name": "Mesa 1",
      "desk_color": "#16a085",
      "call_token": "2026-06-29 10:35:00"
    },
    {
      "number": "A043",
      "desk_name": "Mesa 2",
      "desk_color": "#8e44ad",
      "call_token": "2026-06-29 10:35:12"
    }
  ],
  "next": ["A044", "A045", "A046"]
}
```

Con **varias mesas** en la misma cola, `active_calls` lista todas las atenciones en curso.

## Rellamada

Cuando empleado pulsa **Rellamar** en panel:

1. Backend actualiza `call_date` del ticket
2. `call_token` en display_state cambia
3. `display_app.js` detecta cambio → muestra overlay de nuevo (sonido opcional)

**Importante:** recarga forzada (`Cmd+Shift+R`) si no ves rellamadas tras actualizar módulo.

## Despliegue en TV

### Smart TV / Chromecast

Abrir URL display en navegador integrado. Bookmark + inicio automático si el TV lo permite.

### PC + HDMI

```
Mini PC → Chrome kiosk mode:
chrome --kiosk --app=https://servidor/ticketmaton/display/1/TOKEN
```

### Raspberry Pi

Chromium en modo kiosk apuntando a URL display.

## Varias colas en pantalla

Si la estación tiene Atención + Recogida, la pantalla muestra **una tarjeta por cola**, cada una con su turno actual y siguientes.

```
┌─────────────┐  ┌─────────────┐
│  Atención   │  │  Recogida   │
│    A042     │  │    R015     │
│  A043 A044  │  │  R016 R017  │
└─────────────┘  └─────────────┘
```

## Sin contenido / pantalla vacía

| Causa | Solución |
|-------|----------|
| Sin colas en estación | Crear colas |
| Token incorrecto | Usar URL del formulario estación |
| JS cacheado | Hard refresh |
| Estación archivada | Reactivar estación |

## Verificar con curl

```bash
curl -s -X POST http://localhost:8069/ticketmaton/1/TOKEN/display_state \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}' \
  | python3 -m json.tool
```

Debe devolver `"queues": [...]` con al menos un elemento.
