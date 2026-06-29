# 08 — Panel empleado

URL: `/ticketmaton/control/<station_id>/<token>`

Dispositivo: tablet o móvil en mostrador. No requiere login Odoo.

## Interfaz

```
┌─────────────────────────────────────────┐
│  Panel — Tienda Málaga                  │
│  Soy: [ Mesa 1 ▼ ]                      │
├─────────────────────────────────────────┤
│  Cola: Atención          En espera: 5   │
│  Actual: A041 (Mesa 2)                  │
│  Siguiente: A042, A043, A044              │
│                                         │
│  [ SIGUIENTE ] [ Rellamar ] [ Saltar ]  │
├─────────────────────────────────────────┤
│  Cola: Recogida          En espera: 2   │
│  ...                                    │
└─────────────────────────────────────────┘
```

## Selector de mesa

- Dropdown **"Soy: …"** arriba
- Lista mesas activas de la estación (`desks` en `control_state`)
- Guardado en `localStorage` clave por estación
- Cada mostrador debe elegir **su** mesa

### Ejemplo

```
Tablet izquierda  → localStorage desk_id = 3 (Mesa 1)
Tablet derecha    → localStorage desk_id = 4 (Mesa 2)
```

## Botones por cola

### SIGUIENTE

Llama al siguiente ticket `waiting` de la cola (FIFO por `create_date`).

```
POST /ticketmaton/<id>/<token>/call_next
Params: { queue_id: 1, desk_id: 3 }
```

Efecto:
- Ticket → `state=calling`
- `desk_id` = mesa seleccionada
- `call_date` = ahora
- Pantalla TV muestra overlay
- Bus notifica `ticket_calling`

**Sin turnos en espera:** error `no_waiting`.

### Rellamar

Repite aviso del turno **activo de tu mesa** en esa cola.

```
POST /ticketmaton/<id>/<token>/recall
Params: { queue_id: 1, desk_id: 3 }
```

Busca ticket en `calling`/`serving` con ese `desk_id`. Actualiza `call_date` → overlay en TV.

**Sin turno activo en tu mesa:** error `no_active`.

### Saltar

1. Marca turno actual de tu mesa como `skipped`
2. Llama automáticamente al siguiente en espera

```
POST /ticketmaton/<id>/<token>/skip
Params: { queue_id: 1, desk_id: 3 }
```

Útil cuando cliente no se presenta.

## Estado del panel (`control_state`)

```json
{
  "station_name": "Tienda Málaga",
  "desks": [
    {"id": 3, "name": "Mesa 1", "color": "#16a085", "queue_ids": []},
    {"id": 4, "name": "Mesa 2", "color": "#8e44ad", "queue_ids": []}
  ],
  "queues": [
    {
      "id": 1,
      "name": "Atención",
      "waiting_total": 5,
      "next": ["A042", "A043"],
      "active_calls": [
        {"number": "A041", "desk_id": 4, "desk_name": "Mesa 2"}
      ]
    }
  ]
}
```

## Flujo típico jornada

```
1. Empleado abre panel, elige "Mesa 1"
2. Cliente saca A042 en kiosco
3. Empleado pulsa SIGUIENTE en Atención
4. TV: "Pase a mostrador — A042 — Mesa 1"
5. Cliente llega → atiende
6. Empleado pulsa SIGUIENTE otra vez (o ticket pasa a done en backend)
7. Si cliente no viene → Saltar
8. Si no oyó → Rellamar
```

## Varias colas

Panel muestra **un bloque por cola**. Cada bloque tiene sus propios botones SIGUIENTE/RELLAMAR/SALTAR.

Empleado en mesa sin restricción ve y opera todas las colas.

## Mesa con colas restringidas

Si Mesa 1 solo atiende "Recogida":
- `queue_ids: [2]` en desk
- Panel filtra (frontend) qué colas muestra según mesa seleccionada

## Sin login Odoo

El panel es **público con token**. Cualquiera con la URL puede llamar turnos.

**Riesgo:** si la URL se filtra, alguien externo podría manipular cola.

**Mitigación práctica:**
- No publicar URL panel en redes
- Usar tablet dedicada sin compartir enlace
- Futuro: PIN por mesa (no implementado aún)

## Verificar API

```bash
# Estado
curl -s -X POST http://localhost:8069/ticketmaton/1/TOKEN/control_state \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}'

# Llamar siguiente (cola 1, mesa 3)
curl -s -X POST http://localhost:8069/ticketmaton/1/TOKEN/call_next \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"queue_id":1,"desk_id":3},"id":1}'
```
