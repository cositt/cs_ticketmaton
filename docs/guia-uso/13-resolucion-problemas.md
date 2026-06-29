# 13 — Resolución de problemas

## Kiosco / pantalla

### Kiosco muestra bienvenida pero sin botones

**Causa:** Estación sin colas activas.

**Verificar:**
```bash
curl -s -X POST http://localhost:8069/ticketmaton/STATION_ID/TOKEN/config \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}' | grep queues
```

**Solución:** Crear cola en **esa** estación (pestaña Colas).

---

### Pantalla TV vacía (solo fondo)

Misma causa: `queues: []` en display_state.

**Solución:** Colas en estación correcta. Colas no se comparten entre estaciones.

---

### Pantalla no actualiza al llamar

1. Hard refresh: `Cmd+Shift+R` / `Ctrl+Shift+R`
2. Verificar URL display de la misma estación que el panel
3. Comprobar `display_state` devuelve `current` con valor

---

### Rellamar no muestra overlay

**Causa histórica:** JS antiguo sin detección de `call_token`.

**Solución:** Actualizar módulo + hard refresh pantalla.

**Verificar:** `call_token` cambia en display_state tras rellamar.

---

### Solo se ve fondo de color (sin UI)

**Causa:** JS no cargaba (assets pipeline).

**Estado actual:** JS servido como scripts estáticos en template. Si persiste:
- Ver consola navegador (F12)
- Confirmar rutas `/cs_ticketmaton/static/src/js/*.js` responden 200

---

## Mesas y colas

### Creé mesas pero no funcionan

**Causa:** Mesas no crean colas. Sin cola = sin turnos.

**Checklist:**
```
□ Cola en la misma estación que las mesas
□ Cola active = True
□ Mesas active = True
```

---

### Dos mesas pero una sola cola visible

Correcto si solo hay una cola. Incorrecto si esperabas dos filas → crear segunda cola.

---

### Mesa llama turnos de cola equivocada

Revisar **Colas que atiende** en mesa. Vacío = todas. Con selección = solo esas.

---

## Panel empleado

### SIGUIENTE no hace nada

**Respuesta API:** `{"error": "no_waiting"}`

**Causa:** No hay tickets en espera en esa cola.

**Solución:** Sacar turno en kiosco primero.

---

### Dos empleados llaman el mismo turno

No debería ocurrir: `create_ticket` y `call_next` usan bloqueo SQL (`FOR UPDATE`).

Si ocurre: reportar bug con logs Odoo.

---

### Mesa no guardada entre sesiones

`localStorage` por navegador. Modo incógnito o borrar datos → re-elegir mesa.

---

## Impresión

### No imprime

| Verificar | Acción |
|-----------|--------|
| print_mode | No sea `none` |
| Consola JS | Errores printer.js |
| Web Serial | Chrome + HTTPS o localhost |
| Agente local | `curl -X POST http://127.0.0.1:9101/print` |

---

### Agente local error 500

- Puerto serie incorrecto (`COM3` vs `COM4`)
- `pyserial` no instalado para modo `--serial`
- Impresora apagada

---

## Numeración

### Cola agotada (max alcanzado)

```
UserError: Cola Atención agotada (max 999)
```

**Solución:** Reset contador o subir `max_value` o política reset diario.

---

### Números duplicados

No debería ocurrir con bloqueo actual. Si ocurre:
- Revisar si hay scripts externos creando tickets
- Logs PostgreSQL por deadlocks

---

### JSON multi-segmento inválido

```
UserError: Reglas multi-segmento JSON invalidas
```

Validar JSON en [jsonlint.com](https://jsonlint.com). Comillas dobles obligatorias.

---

## Odoo / técnico

### 404 en URLs ticketmaton

- `station_id` incorrecto
- `token` no coincide con `access_token` de estación
- Estación borrada

---

### Módulo no aparece

```
Actualizar lista aplicaciones
Modo desarrollador activo
Ruta addons incluye custom-addons
```

---

### Actualizar módulo

```bash
docker exec odoo19_runtime odoo -c /etc/odoo/odoo.conf -d odoo -u cs_ticketmaton --stop-after-init
docker restart odoo19_runtime
```

---

## Diagnóstico rápido con curl

```bash
STATION=1
TOKEN=tu-token-aqui
BASE=http://localhost:8069

# Config kiosco
curl -s -X POST $BASE/ticketmaton/$STATION/$TOKEN/config \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}' | python3 -m json.tool

# Estado pantalla
curl -s -X POST $BASE/ticketmaton/$STATION/$TOKEN/display_state \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}' | python3 -m json.tool

# Sacar ticket (queue_id=1)
curl -s -X POST $BASE/ticketmaton/$STATION/$TOKEN/take_ticket \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"queue_id":1},"id":1}' | python3 -m json.tool

# Llamar siguiente
curl -s -X POST $BASE/ticketmaton/$STATION/$TOKEN/call_next \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"queue_id":1,"desk_id":3},"id":1}' | python3 -m json.tool
```

Sustituir `STATION`, `TOKEN`, `queue_id`, `desk_id` por valores reales del formulario estación.
