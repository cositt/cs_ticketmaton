# 09 — Impresión térmica

Configuración en **Estación → grupo Impresión**.

## Modos disponibles

| Modo | Código | Cuándo usar |
|------|--------|-------------|
| Navegador | `browser` | Fallback universal (`window.print`) |
| ESC/POS Web Serial | `escpos_serial` | Chrome/Edge + impresora USB |
| Android WebView Bridge | `android_bridge` | Kiosco Android con app nativa |
| QZ Tray | `qz_tray` | Windows con [QZ Tray](https://qz.io/) |
| Agente local HTTP | `local_agent` | Script Python en PC del kiosco |
| Sin impresión | `none` | Solo pantalla |

## Campos comunes

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Modo impresión | Selector anterior | escpos_serial |
| Cabecera ticket | Texto impreso arriba | FARMACIA NORTE |
| Ancho papel | 58mm o 80mm | 58 |
| URL agente local | Solo modo local_agent | http://127.0.0.1:9101/print |
| Nombre impresora QZ | Solo modo qz_tray | EPSON_TM_T20 |

## Contenido del ticket impreso

Generado por `TicketmatonEscPosBuilder` (`escpos.js`):

```
================================
        TICKETMATON
      Tienda Málaga
      Atención
================================

         A042

      29/06/2026 10:30

Espere a que se llame su numero
================================
```

Datos desde `ticket.get_print_data()`.

---

## Modo 1: Navegador (`browser`)

**Configuración:**

```
Modo impresión: Navegador
```

**Uso:** abre diálogo de impresión del navegador con CSS optimizado para papel estrecho.

**Pros:** funciona en cualquier navegador  
**Contras:** requiere interacción usuario; no ideal en kiosco desatendido

---

## Modo 2: ESC/POS Web Serial (`escpos_serial`)

**Configuración:**

```
Modo impresión: ESC/POS Web Serial
Ancho: 58mm
```

**Requisitos:**
- Chrome o Edge (Web Serial API)
- Impresora térmica USB
- Primera vez: navegador pide permiso de puerto serie

**Flujo:**
1. Cliente saca turno
2. `printer.js` → `navigator.serial.requestPort()`
3. Envía bytes ESC/POS a 9600 baud

**Ejemplo kiosco Windows:**

```
Tablet Windows 11 + Chrome
Impresora Epson TM-T20 USB
Estación → escpos_serial, 58mm
```

Si Web Serial falla → fallback automático a `browser`.

---

## Modo 3: Android Bridge (`android_bridge`)

**Configuración:**

```
Modo impresión: Android WebView Bridge
```

**Requisitos:** app Android con WebView que exponga:

```java
webView.addJavascriptInterface(new Object() {
    @JavascriptInterface
    public void printEscPos(String base64) {
        byte[] data = Base64.decode(base64, Base64.DEFAULT);
        // enviar a impresora USB/BT del kiosco
    }
}, "TicketmatonAndroid");
```

**Alternativas detectadas por el JS:**
- `window.TicketmatonAndroid.printEscPos(base64)`
- `window.AndroidBridge.postMessage(...)`
- Custom URL `ticketmaton://print?data=...`

---

## Modo 4: QZ Tray (`qz_tray`)

**Configuración:**

```
Modo impresión: QZ Tray
Nombre impresora QZ: EPSON_TM_T20
```

**Requisitos:**
1. Instalar [QZ Tray](https://qz.io/) en Windows del kiosco
2. Cargar script QZ en página (si no está, fallback browser)
3. Nombre exacto de impresora en Windows

**Ejemplo:**

```
PC kiosco Windows 10
QZ Tray 2.x en bandeja sistema
Impresora compartida "EPSON_TM_T20"
```

---

## Modo 5: Agente local HTTP (`local_agent`)

**Configuración estación:**

```
Modo impresión: Agente local HTTP
URL agente: http://127.0.0.1:9101/print
```

**Arrancar agente** (en PC del kiosco):

```bash
cd custom-addons/cs_ticketmaton/tools

# Impresora USB Windows
pip install pyserial
python3 print_agent.py --serial COM3

# Impresora USB Linux
python3 print_agent.py --serial /dev/usb/lp0

# Impresora red (puerto raw 9100)
python3 print_agent.py --tcp 192.168.1.50:9100

# Puerto HTTP distinto
python3 print_agent.py --tcp 192.168.1.50:9100 --port 9102
```

**Protocolo POST:**

```http
POST /print HTTP/1.1
Content-Type: application/json

{"data": "<base64 ESC/POS>"}
```

Respuesta OK: `{"ok": true}`

**Ejemplo completo tienda:**

```
1. Mini PC junto al kiosco con impresora USB
2. Agente: python3 print_agent.py --serial COM3
3. Estación Odoo: local_agent, URL http://127.0.0.1:9101/print
4. Tablet kiosco apunta a Odoo; al imprimir POST va a localhost del mini PC
```

> Si kiosco y agente están en máquinas distintas, cambiar `127.0.0.1` por IP del PC con impresora y abrir firewall puerto 9101.

---

## Modo 6: Sin impresión (`none`)

```
Modo impresión: Sin impresion
```

Solo muestra número en pantalla kiosco. Útil si la TV o pantalla del kiosco es suficiente.

---

## Comparativa rápida

| Escenario | Modo recomendado |
|-----------|------------------|
| Prueba rápida | browser o none |
| Kiosco Windows + USB | escpos_serial |
| Kiosco Android comercial | android_bridge |
| Windows empresa con QZ | qz_tray |
| Red / impresora compartida | local_agent + --tcp |
| Sin papel | none |

## Troubleshooting impresión

| Problema | Causa | Solución |
|----------|-------|----------|
| No imprime nada | mode=none | Cambiar modo |
| Pide puerto cada vez | Web Serial sin permiso persistente | Chrome flags / kiosk policy |
| Agente 500 | Puerto serie incorrecto | Verificar COM/dev |
| QZ no encontrado | Script no cargado | Instalar QZ Tray |
| Ticket en blanco | Ancho mal (58 vs 80) | Ajustar ticket_print_width |
| CORS agente | URL no es localhost | Mismo origen o proxy |
