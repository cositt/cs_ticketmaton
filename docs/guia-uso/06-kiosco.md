# 06 — Kiosco (pantalla cliente)

URL: `/ticketmaton/kiosk/<station_id>/<token>`

Dispositivo: tablet táctil en entrada. El cliente saca turno pulsando un botón.

## Flujo de pantallas

```
┌─────────────────┐     pulsa botón      ┌─────────────────┐
│   BIENVENIDA    │ ──────────────────►  │  TU TURNO ES    │
│  [Atención]     │                      │     A042        │
│  [Recogida]     │                      │  (impresión)    │
└─────────────────┘                      └─────────────────┘
        ▲                                         │
        └──────── timeout / nueva pulsación ◄─────┘
```

## Qué carga al abrir

1. Template QWeb `kiosk_page`
2. Scripts estáticos: `escpos.js`, `printer.js`, `kiosk_app.js`
3. Llamada JSON-RPC `config` → colas, estilos, mensajes
4. Suscripción bus Odoo para actualizaciones (opcional)

## Elementos visibles

| Elemento | Origen config |
|----------|---------------|
| Título | `welcome_message` |
| Subtítulo | `subtitle_message` |
| Logo | Campo imagen estación |
| Botones | Una por cola activa |
| Fondo | `bg_color`, `theme` |

### Personalización botones (por cola)

- Texto: `button_label` o nombre cola
- Color fondo: `button_color`
- Color texto: `button_text_color`
- Icono: `button_icon`
- Radio bordes: `button_radius` (estación)

## Sacar turno

Al pulsar botón:

```
POST /ticketmaton/<id>/<token>/take_ticket
Body: { queue_id: 3 }
```

Respuesta:

```json
{
  "ticket": {
    "id": 42,
    "number": "A042",
    "queue_name": "Atención",
    "state": "waiting"
  },
  "print_data": {
    "header": "TICKETMATON",
    "number": "A042",
    "date": "29/06/2026 10:30",
    "width_mm": 58
  }
}
```

Pantalla muestra:
- `ticket_header` + número grande
- `ticket_footer` abajo
- Impresión según `print_mode` (ver cap. 09)

## Ejemplo: configurar kiosco tienda bebé

**Estación:**

| Campo | Valor |
|-------|-------|
| Mensaje bienvenida | Bienvenido a Bebé Málaga |
| Subtítulo | Seleccione su servicio |
| Texto ticket | Su turno es |
| Pie ticket | Espere a que se llame su número |
| Tema | Claro |
| Color fondo | #1a5276 |
| Radio botones | 16 |
| Tamaño texto botones | 28 |

**Cola Atención:**

| Campo | Valor |
|-------|-------|
| Etiqueta botón | Atención al cliente |
| Color | #2980b9 |
| Icono | fa-child |

**Despliegue:**

1. Tablet Android → Chrome → URL kiosco
2. Añadir a pantalla inicio
3. Modo kiosco / pantalla fijada (guided access iOS, kiosk mode Android)

## Sin botones en kiosco

Causa: `queues` vacío en config → estación sin colas activas.

```bash
# Verificar con curl
curl -s -X POST http://localhost:8069/ticketmaton/1/TOKEN/config \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}' \
  | python3 -m json.tool
```

Buscar `"queues": []` → crear cola en esa estación.

## Impresión desde kiosco

Tras `take_ticket`, `kiosk_app.js` llama `TicketmatonPrinter.print(print_data)`.

Modos: ver [09-impresion-termica.md](09-impresion-termica.md).

## Recomendaciones hardware

| Dispositivo | Notas |
|-------------|-------|
| Tablet 10" | Mínimo para botones táctiles cómodos |
| Impresora 58mm USB | Web Serial en Chrome |
| Kiosco Android | App WebView + bridge nativo |
| Sin impresora | `print_mode: none` — solo pantalla |

## Timeout / vuelta a bienvenida

Tras mostrar el ticket unos segundos, vuelve a pantalla de botones para el siguiente cliente (comportamiento en `kiosk_app.js`).
