# 02 — Conceptos y arquitectura

## Modelo de datos

```
ticketmaton.station     → Estación (punto de atención)
    ├── ticketmaton.queue   → Cola (tipo de servicio / pool de turnos)
    ├── ticketmaton.desk    → Mesa / mostrador
    └── ticketmaton.ticket  → Ticket individual
```

## Estación

Unidad de configuración. Una tienda = una estación. Cada estación tiene:

- Sus propias colas (no se comparten entre estaciones)
- Sus propias mesas
- Sus propias 3 URLs (kiosco, pantalla, panel)
- Token de acceso único para las URLs públicas

**Ejemplo:** Tienda Málaga y Tienda Sevilla = 2 estaciones independientes.

## Cola

Pool de turnos de un tipo de servicio. El cliente elige cola en el kiosco (un botón por cola).

| Concepto | Analogía |
|----------|----------|
| Cola "Atención" | Fila para hablar con un dependiente |
| Cola "Recogida" | Fila para recoger pedidos |
| Cola "Caja" | Fila para pagar |

Cada cola tiene su propia numeración (000, A001, etc.).

## Mesa / Mostrador

Punto físico donde atiende un empleado. **No crea turnos** — solo los llama desde el pool de una cola.

**Clave:** Varias mesas pueden atender **la misma cola**. Mesa 1 y Mesa 2 comparten el pool; cada una pulsa SIGUIENTE y coge el siguiente turno disponible.

```
Cola "Atención":  [A040] [A041] [A042] [A043] ...
                        ↑        ↑
                     Mesa 1   Mesa 2   (llaman en paralelo)
```

## Ticket

Turno individual con estados:

```
waiting → calling → serving → done
   │         │          │
   │         │          └── Atendiendo al cliente
   │         └── Llamado en pantalla
   └── En espera (sacado en kiosco)

También: skipped (saltado), cancelled (cancelado)
```

## Las 3 pantallas web

| Pantalla | Ruta | Usuario | Función |
|----------|------|---------|---------|
| Kiosco | `/ticketmaton/kiosk/<id>/<token>` | Cliente | Sacar turno |
| Pantalla | `/ticketmaton/display/<id>/<token>` | Público (TV) | Ver turno actual |
| Panel | `/ticketmaton/control/<id>/<token>` | Empleado | Llamar siguiente |

El `<token>` es el `access_token` de la estación (UUID). Sin token válido → 404.

## Flujo completo

```
1. Cliente pulsa botón en KIOSCO
   → Se crea ticket (state=waiting)
   → Se imprime ticket (opcional)
   → Pantalla kiosco muestra el número

2. Empleado pulsa SIGUIENTE en PANEL (elige su mesa)
   → Ticket pasa a calling
   → Se asigna desk_id (mesa)
   → PANTALLA muestra overlay "A042 → Mesa 1"

3. Cliente pasa al mostrador
   → Empleado pulsa SIGUIENTE otra vez (o Finalizar en backend)
   → Ticket pasa a done
   → Siguiente turno en espera queda visible en pantalla
```

## Qué NO es

| Confusión | Realidad |
|-----------|----------|
| Una cola por mesa | Incorrecto si quieres fila única. Una cola, N mesas |
| Mesas en distinta estación comparten cola | No. Colas pertenecen a una estación |
| Panel requiere login Odoo | No. URL pública con token (como kiosco) |
| WooCommerce / colas sync | Módulo independiente, solo turnos físicos |
