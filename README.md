# Ticketmaton — Sistema de turnos para Odoo 19

Módulo de dispensador de turnos con kiosco táctil, pantalla pública, panel de empleado e impresión térmica.

## Documentación completa

- **Online:** [https://cositt.github.io/cs_ticketmaton_documentacion/](https://cositt.github.io/cs_ticketmaton_documentacion/)
- **Repositorio:** [github.com/cositt/cs_ticketmaton_documentacion](https://github.com/cositt/cs_ticketmaton_documentacion)
- **En el módulo:** [docs/guia-uso/](docs/guia-uso/README.md)

14 capítulos: instalación, colas, mesas, kiosco, pantalla TV, panel empleado, impresión, API y troubleshooting.

## Qué hace

Gestiona turnos físicos en tienda o mostrador:

1. **Cliente** saca ticket en el kiosco (pantalla táctil).
2. **Empleado** llama al siguiente desde el panel de control.
3. **Pantalla pública** (TV) muestra el turno actual y avisa con overlay al llamar o rellamar.
4. Opcionalmente se **imprime ticket** en impresora térmica.

## Las 3 pantallas

Cada **estación** tiene 3 URLs (visibles en el formulario de la estación):

| Pantalla | URL | Quién la usa |
|----------|-----|--------------|
| **Kiosco** | `/ticketmaton/kiosk/<id>/<token>` | Cliente (tablet/kiosco en entrada) |
| **Pantalla pública** | `/ticketmaton/display/<id>/<token>` | TV en sala de espera |
| **Panel empleado** | `/ticketmaton/control/<id>/<token>` | Mostrador (tablet/móvil) |

El `<token>` es el identificador de seguridad de la estación (campo `access_token`, generado automáticamente).

## Conceptos clave

```
Estación
 ├── Cola(s)          → tipos de servicio (Atención, Recogida…)
 ├── Mesa(s)          → mostradores que atienden (Mesa 1, Mesa 2…)
 └── Ticket(s)        → turnos generados
```

### Cola vs Mesa (importante)

- **Cola** = el pool de turnos. El cliente saca un número de una cola.
- **Mesa** = el mostrador que atiende. Varias mesas pueden atender **la misma cola**.

Ejemplo real: una tienda con 2 mostradores y una sola fila de atención:

```
Estación "Tienda Centro"
 └── Cola "Atención"          ← UNA sola cola
      ├── Mesa 1              ← ambas atienden la misma cola
      └── Mesa 2
```

El cliente saca turno `A042`. Mesa 1 pulsa SIGUIENTE → llama `A042` y la pantalla dice **"A042 → Mesa 1"**. Mesa 2 pulsa SIGUIENTE → llama `A043` (el siguiente del mismo pool).

**No crees una cola por mesa** salvo que quieras filas separadas (Atención vs Recogida).

## Primera configuración (paso a paso)

### 1. Instalar el módulo

En Odoo: **Aplicaciones** → buscar **Ticketmaton** → Instalar.

Requisitos: `base`, `web`, `bus`, `website`.

### 2. Crear una estación

**Ticketmaton → Estaciones → Crear**

| Campo | Ejemplo |
|-------|---------|
| Nombre | Tienda Málaga |
| Mensaje bienvenida | Bienvenido a nuestra tienda |
| Subtítulo | Pulse para sacar turno |
| Prefijo llamada pantalla | Pase a mostrador |

Guardar. Aparecen las 3 URLs en el formulario.

### 3. Crear cola(s)

En la pestaña **Colas** de la estación:

**Ejemplo A — Numeración simple (000-999):**

| Campo | Valor |
|-------|-------|
| Nombre | Atención al cliente |
| Código | ATN |
| Tipo numeración | Numérico |
| Padding | 3 |
| Mín / Máx | 0 / 999 |
| Reset | Diario |
| Etiqueta botón | Atención |
| Color botón | #2980b9 |

**Ejemplo B — Con prefijo (A000-A999):**

| Campo | Valor |
|-------|-------|
| Tipo numeración | Con prefijo |
| Prefijo | A |
| Padding | 3 |
| Mín / Máx | 0 / 999 |

**Ejemplo C — Multi-segmento (A00-A99, luego B01-B99):**

| Campo | Valor |
|-------|-------|
| Tipo numeración | Multi-segmento |
| Reglas JSON | `[{"prefix":"A","min":0,"max":99,"padding":2},{"prefix":"B","min":1,"max":99,"padding":2}]` |

Si necesitas **varios tipos de servicio** (Atención + Recogida), crea **varias colas** en la misma estación. El kiosco mostrará un botón por cola.

### 4. Crear mesas (opcional pero recomendado)

En la pestaña **Mesas / Mostradores**:

| Mesa | Color | Colas que atiende |
|------|-------|-------------------|
| Mesa 1 | #16a085 | *(vacío = todas)* |
| Mesa 2 | #8e44ad | *(vacío = todas)* |

Dejar **"Colas que atiende" vacío** = la mesa atiende todas las colas de la estación.

Solo rellenar ese campo si quieres limitar una mesa a colas concretas (ej. Mesa 1 solo Recogida).

### 5. Abrir las pantallas

Desde el formulario de la estación, botones del header:

- **Abrir Kiosco** → pantalla completa en tablet de entrada
- **Abrir Pantalla** → pantalla completa en TV
- **Abrir Panel Empleado** → pantalla en tablet de mostrador

Recomendación: abrir cada URL en el dispositivo correspondiente y marcar como favorita. Usar modo kiosco del navegador si está disponible.

### 6. Panel empleado — elegir mesa

Al abrir el panel, arriba aparece **"Soy: Mesa X"**. Cada mostrador elige su mesa. La selección se guarda en el navegador (localStorage).

Botones por cola:

| Botón | Acción |
|-------|--------|
| **SIGUIENTE** | Llama al siguiente turno en espera y lo asigna a tu mesa |
| **Rellamar** | Vuelve a avisar en pantalla el turno actual de tu mesa |
| **Saltar** | Descarta el turno actual y llama al siguiente |

## Flujo operativo diario

```
Cliente                    Empleado                  Pantalla TV
   │                          │                          │
   ├─ Pulsa botón kiosco      │                          │
   ├─ Sale ticket impreso     │                          │
   ├─ Ve su número            │                          │
   │                          ├─ Pulsa SIGUIENTE        │
   │                          │   (elige su mesa)       │
   │                          │                          ├─ Overlay: "A042 → Mesa 1"
   │◄─ Pasa a mostrador───────┤                          │
```

## Impresión térmica

Configurar en la estación → grupo **Impresión**:

| Modo | Cuándo usarlo |
|------|---------------|
| **Navegador** | Fallback universal (`window.print`) |
| **ESC/POS Web Serial** | Chrome/Edge con impresora USB (Web Serial API) |
| **Android WebView Bridge** | Kiosco Android con app wrapper (`window.TicketmatonAndroid.printEscPos`) |
| **QZ Tray** | Windows con [QZ Tray](https://qz.io/) instalado |
| **Agente local HTTP** | Script Python incluido en `tools/print_agent.py` |
| **Sin impresión** | Solo pantalla, sin papel |

### Agente local (ejemplo)

```bash
# Impresora USB (Windows)
python3 tools/print_agent.py --serial COM3

# Impresora de red (puerto raw 9100)
python3 tools/print_agent.py --tcp 192.168.1.50:9100
```

En la estación, modo **Agente local HTTP** y URL `http://127.0.0.1:9101/print`.

### Android bridge (ejemplo)

```java
webView.addJavascriptInterface(new Object() {
    @JavascriptInterface
    public void printEscPos(String base64) {
        byte[] data = Base64.decode(base64, Base64.DEFAULT);
        // enviar bytes a impresora USB/BT del kiosco
    }
}, "TicketmatonAndroid");
```

## Personalización visual

Todo configurable desde el formulario de estación, sin tocar código:

| Pestaña | Qué personaliza |
|---------|-----------------|
| Mensajes kiosco | Bienvenida, subtítulo, textos del ticket |
| Estilo kiosco | Colores, radio botones, tamaño fuente, logo |
| Pantalla pública | Colores, tamaño número, etiquetas, prefijo de llamada |
| Colas (inline) | Texto botón, color, icono FontAwesome por cola |

## Backend Odoo

Además de las pantallas web, el módulo tiene menú en Odoo:

- **Ticketmaton → Panel** — lista/kanban de tickets activos
- **Ticketmaton → Estaciones** — configuración
- **Ticketmaton → Colas** — gestión de colas

Útil para supervisión, historial y acciones manuales.

## Ejemplo completo: tienda con 2 mostradores

```
Estación: "Bebé Málaga"
│
├── Cola "Atención" (A000-A999, reset diario)
│
├── Mesa 1 (sin restricción de colas)
├── Mesa 2 (sin restricción de colas)
│
├── Kiosco    → tablet en entrada
├── Pantalla  → TV en sala de espera
└── Panel     → tablet en cada mostrador (cada uno elige su mesa)
```

URLs (sustituir `<id>` y `<token>` por los de tu estación):

```
http://tu-servidor/ticketmaton/kiosk/<id>/<token>
http://tu-servidor/ticketmaton/display/<id>/<token>
http://tu-servidor/ticketmaton/control/<id>/<token>
```

## Resolución de problemas

### Kiosco muestra bienvenida pero sin botones

La estación **no tiene colas**. Crear al menos una cola en la pestaña Colas de la estación.

### Pantalla vacía

Misma causa: sin colas en la estación. Las colas pertenecen a una estación concreta; no se comparten entre estaciones.

### Creé mesas pero no funcionan

Las mesas no crean colas. Necesitas:

1. Al menos **una cola** en la estación.
2. Mesas con **"Colas que atiende" vacío** (atienden todas) o vinculadas a colas de **esa misma estación**.

### Rellamar no avisa en pantalla

Recargar la pantalla con `Cmd+Shift+R` (o `Ctrl+Shift+R`) para cargar el JS actualizado.

### Varias mesas, misma cola — ¿cómo?

- **Una cola** en la estación (no una por mesa).
- **Varias mesas**, sin restricción de colas.
- Cada mostrador abre el panel y elige su mesa.
- Cada mesa pulsa SIGUIENTE de forma independiente; cogen turnos del mismo pool.

## Estructura del módulo

```
cs_ticketmaton/
├── models/
│   ├── ticketmaton_station.py   # Estación (config global)
│   ├── ticketmaton_queue.py     # Cola + motor numeración
│   ├── ticketmaton_desk.py      # Mesa/mostrador
│   └── ticketmaton_ticket.py    # Ticket individual
├── controllers/main.py          # Rutas web + API JSON-RPC
├── static/src/
│   ├── js/kiosk_app.js          # Kiosco cliente
│   ├── js/display_app.js        # Pantalla pública
│   ├── js/control_app.js        # Panel empleado
│   ├── js/printer.js            # Impresión multi-plataforma
│   └── js/escpos.js             # Generador ESC/POS
├── tools/print_agent.py         # Agente impresión local
└── views/                       # Vistas Odoo + templates QWeb
```

## Licencia

LGPL-3
