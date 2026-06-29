# 12 — Casos prácticos

Escenarios reales paso a paso.

---

## Caso 1: Tienda con 2 mostradores, una fila

**Necesidad:** Un solo tipo de atención. Dos empleados atienden en paralelo.

### Configuración

```
Estación: "Tienda Centro"
├── Cola "Atención"
│     Tipo: prefijo A, padding 3, reset diario
├── Mesa 1 (colas: vacío)
└── Mesa 2 (colas: vacío)
```

### Despliegue

| Dispositivo | URL |
|-------------|-----|
| Tablet entrada | kiosk |
| TV | display |
| Tablet mostrador 1 | control → Mesa 1 |
| Tablet mostrador 2 | control → Mesa 2 |

### Operación

1. Cliente saca A050
2. Mesa 1 → SIGUIENTE → TV: "A050 → Mesa 1"
3. Cliente saca A051
4. Mesa 2 → SIGUIENTE → TV: "A051 → Mesa 2"
5. Ambos atienden en paralelo

---

## Caso 2: Atención + Recogida (dos filas)

**Necesidad:** Cliente elige si necesita información o recoger pedido.

### Configuración

```
Estación: "Bebé Málaga"
├── Cola "Atención" (A000, botón azul)
├── Cola "Recogida" (R000, botón verde, prefijo R)
├── Mesa 1 → colas: [Atención]
└── Mesa 2 → colas: [Recogida]
```

### Kiosco

Dos botones. Cliente pulsa según necesidad.

### Panel

- Mostrador info: Mesa 1, solo ve cola Atención
- Mostrador recogida: Mesa 2, solo ve cola Recogida

---

## Caso 3: Farmacia sin impresora

**Necesidad:** Solo pantalla. Cliente memoriza número o mira ticket en kiosco.

### Configuración

```
print_mode: none
Cola: Numérico 001-999
welcome_message: Farmacia San Juan
```

Tablet en mostrador muestra número grande tras pulsar. TV en sala muestra llamadas.

---

## Caso 4: Kiosco Android con impresora integrada

**Necesidad:** App kiosco propia imprime por USB.

### Configuración Odoo

```
print_mode: android_bridge
ticket_print_width: 58
```

### App Android

WebView carga URL kiosco. Interface `TicketmatonAndroid.printEscPos(base64)`.

### Prueba

1. Sacar turno en kiosco
2. Verificar ticket físico con número y fecha

---

## Caso 5: Windows + QZ Tray + Epson

### Configuración

```
print_mode: qz_tray
qz_printer_name: EPSON_TM_T20
ticket_print_width: 80
```

### Pasos

1. Instalar QZ Tray en PC kiosco
2. Compartir impresora Epson
3. Copiar nombre exacto a Odoo
4. Probar impresión desde kiosco

---

## Caso 6: Reinicio de numeración cada mañana

### Configuración

```
Estación reset_hour: 8.0  (8:00 AM)
Cola reset_policy: daily
min_value: 1
padding: 3
```

A las 8:00 del día siguiente: vuelve a 001 (o A001 según tipo).

---

## Caso 7: Recuperar tras pruebas

Borraste tickets de prueba y quieres empezar limpio:

```
1. Estación → Reset contadores
2. Opcional: archivar tickets viejos en backend
3. Verificar kiosco saca 001 o A001
```

---

## Caso 8: Cliente no se presenta

```
1. Empleado esperó, cliente no viene
2. Panel → Saltar
3. Sistema marca ticket skipped y llama siguiente automáticamente
```

---

## Caso 9: Cliente no oyó la llamada

```
1. Panel → Rellamar
2. TV muestra overlay otra vez con mismo número
3. Repetir si necesario
```

---

## Caso 10: Multi-segmento en día punta

**Necesidad:** Mañana A01-A99, tarde reinicio visual con B01.

### Configuración

```
sequence_type: multi_segment
multi_segment_rules:
[
  {"prefix":"A","min":1,"max":99,"padding":2},
  {"prefix":"B","min":1,"max":99,"padding":2}
]
reset_policy: manual
```

Al mediodía: **Reset contador** manual en cola o estación.

---

## Checklist puesta en marcha

```
□ Estación creada con mensajes
□ Al menos 1 cola activa
□ Mesas creadas (si multi-mostrador)
□ URLs abiertas en dispositivos correctos
□ Impresión probada con ticket real
□ Flujo completo: kiosco → panel → TV
□ Empleados saben elegir mesa en panel
□ Reset diario configurado
```
