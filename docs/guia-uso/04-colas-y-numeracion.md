# 04 — Colas y numeración

La **cola** define el tipo de servicio y el formato del número que ve el cliente.

## Crear cola

Desde **Estación → pestaña Colas** o **Ticketmaton → Colas → Crear**.

### Campos obligatorios

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Nombre | Nombre visible | Atención al cliente |
| Código | Código interno único por estación | ATN |
| Estación | A qué estación pertenece | Tienda Málaga |
| Tipo numeración | Ver sección siguiente | Con prefijo |

## Botón en kiosco

| Campo | Vacío = | Ejemplo |
|-------|---------|---------|
| Etiqueta botón | Usa el nombre de la cola | Atención rápida |
| Color botón | #2980b9 | #e74c3c |
| Color texto botón | #ffffff | #000000 |
| Icono | fa-ticket | fa-shopping-bag |

Iconos: clases [Font Awesome 4](https://fontawesome.com/v4/icons/) (`fa-*`).

### Ejemplo: dos servicios distintos

```
Cola "Atención"
  - Etiqueta: Atención al cliente
  - Color: #2980b9 (azul)
  - Icono: fa-user

Cola "Recogida"
  - Etiqueta: Recoger pedido
  - Color: #27ae60 (verde)
  - Icono: fa-shopping-bag
```

Kiosco muestra 2 botones grandes, uno por cola.

## Tipos de numeración

### 1. Numérico (000-999)

Sin prefijo. Relleno con ceros según `padding`.

| Campo | Valor | Resultado |
|-------|-------|-----------|
| Padding | 3 | 000, 001, … 999 |
| Mín | 0 | Empieza en 000 |
| Máx | 999 | Tras 999 → error o reinicio según config |

**Ejemplo secuencia:** `000` → `001` → `002` → … → `042`

### 2. Con prefijo (A00-A99)

Prefijo fijo + número con padding.

| Campo | Valor | Resultado |
|-------|-------|-----------|
| Prefijo | A | A000, A001, … |
| Padding | 3 | Tres dígitos |
| Mín / Máx | 0 / 999 | A000 a A999 |

**Ejemplo secuencia:** `A040` → `A041` → `A042`

### 3. Multi-segmento

Varios rangos con prefijos distintos. Configuración en JSON.

**Campo Reglas JSON (ejemplo):**

```json
[
  {"prefix": "A", "min": 0, "max": 99, "padding": 2},
  {"prefix": "B", "min": 1, "max": 99, "padding": 2}
]
```

**Secuencia resultante:**

```
A00 → A01 → … → A99 → B01 → B02 → … → B99
```

Útil cuando quieres distinguir visualmente fases del día o tipos sin crear colas separadas.

## Política de reset

| Política | Comportamiento |
|----------|----------------|
| Reset diario | Contador vuelve al mínimo cada día (según `reset_hour` estación) |
| Sin reset automático | Nunca reinicia solo; sigue incrementando |
| Solo manual | Solo reinicia con botón "Resetear contadores" |

## Color en pantalla pública

Campo **Color** de la cola → borde/accent en la tarjeta de la pantalla TV.

```
Cola Atención → #3498db (azul)
Cola Recogida → #e67e22 (naranja)
```

## Contador interno

Campos de solo lectura (no editar manualmente salvo reset):

| Campo | Uso |
|-------|-----|
| counter_value | Último valor asignado |
| counter_segment_index | Índice del segmento activo (multi_segment) |
| last_reset_date | Fecha del último reset diario |

## Motor de numeración (cómo funciona)

1. Cliente pulsa botón → `queue.create_ticket()`
2. Se ejecuta `_maybe_reset_counter()` si aplica reset diario
3. Se incrementa contador en transacción (bloqueo)
4. Se formatea número según tipo
5. Se crea `ticketmaton.ticket` con `state=waiting`

## Ejemplos de configuración

### Farmacia: una cola simple

```
Nombre: Mostrador
Código: MOS
Tipo: Numérico
Padding: 3
Min/Max: 1/999
Reset: Diario
```

Tickets: `001`, `002`, `003`…

### Tienda bebé: atención con prefijo A

```
Nombre: Atención
Código: ATN
Tipo: Con prefijo
Prefijo: A
Padding: 3
Min/Max: 0/999
Reset: Diario
```

Tickets: `A000`, `A001`, … `A042`

### Centro médico: dos colas

```
Cola "Consulta"  → prefijo C, padding 3
Cola "Análisis"  → prefijo A, padding 3
```

Cliente elige en kiosco. Cada cola numera independiente.

### Recogida solo tardes (multi-segmento)

```
Tipo: Multi-segmento
Reglas:
[
  {"prefix": "M", "min": 1, "max": 50, "padding": 2},
  {"prefix": "T", "min": 1, "max": 50, "padding": 2}
]
```

Mañana M01-M50, tarde T01-T50 (si reseteas manualmente al mediodía).

## Acciones desde backend

| Acción | Dónde | Efecto |
|--------|-------|--------|
| Resetear contador | Formulario cola | Vuelve contador al mínimo |
| Resetear todos | Formulario estación | Reset en todas las colas |

## Errores frecuentes

| Problema | Causa | Solución |
|----------|-------|----------|
| Kiosco sin botones | 0 colas activas en estación | Crear cola en esa estación |
| Número no avanza | Llegó al máximo | Subir máx o resetear |
| JSON inválido | Reglas multi-segmento mal formadas | Validar JSON en editor |
| Código duplicado | Mismo código en 2 colas de una estación | Códigos únicos por estación |
