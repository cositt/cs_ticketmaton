# 05 — Mesas y mostradores

La **mesa** representa el punto físico donde atiende un empleado. No genera turnos; solo los consume del pool de una cola.

## Concepto clave: varias mesas, una cola

```
        Cola "Atención"
        ┌─────────────────────────┐
        │ A040  A041  A042  A043  │  ← pool compartido
        └─────────────────────────┘
              ↑           ↑
           Mesa 1      Mesa 2
         (llama A040) (llama A041)
```

**Correcto:** 1 cola + N mesas  
**Incorrecto** (si quieres fila única): 1 cola por mesa

## Crear mesa

**Estación → pestaña Mesas / Mostradores → Añadir línea**

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Nombre | Identificador visible | Mesa 1 |
| Secuencia | Orden en selector del panel | 10 |
| Color | Color en pantalla TV al llamar | #16a085 |
| Colas que atiende | Restricción opcional | *(vacío)* |
| Activo | Visible en panel | ✓ |

## Campo "Colas que atiende"

| Valor | Comportamiento |
|-------|----------------|
| **Vacío** | La mesa puede atender **todas** las colas de la estación |
| Con colas seleccionadas | Solo atiende esas colas |

### Ejemplo A: dos mostradores, misma fila (caso típico)

```
Estación "Tienda"
├── Cola "Atención"
├── Mesa 1 → Colas que atiende: (vacío)
└── Mesa 2 → Colas que atiende: (vacío)
```

Ambas pulsan SIGUIENTE en cola Atención. Cada una coge el siguiente turno libre.

### Ejemplo B: especialización por mesa

```
Estación "Tienda"
├── Cola "Atención"
├── Cola "Recogida"
├── Mesa 1 → Colas: [Atención]
└── Mesa 2 → Colas: [Recogida]
```

Mesa 1 solo ve botones/acciones de Atención. Mesa 2 solo Recogida.

### Ejemplo C: una mesa hace de todo, otra solo caja

```
├── Cola "Atención"
├── Cola "Caja"
├── Mesa "Mostrador" → (vacío) = atiende todo
└── Mesa "Caja"      → [Caja]
```

## Uso en panel empleado

1. Empleado abre URL del panel
2. Arriba: selector **"Soy: [Mesa X]"**
3. Selección guardada en `localStorage` del navegador
4. SIGUIENTE / RELLAMAR / SALTAR usan `desk_id` de la mesa elegida

### Ejemplo operativo

```
Mostrador izquierdo → tablet → Panel → "Soy: Mesa 1"
Mostrador derecho   → tablet → Panel → "Soy: Mesa 2"

Mesa 1 pulsa SIGUIENTE → ticket A042, pantalla: "A042 → Mesa 1"
Mesa 2 pulsa SIGUIENTE → ticket A043, pantalla: "A043 → Mesa 2"
```

## Qué ve la pantalla TV

Con varias mesas activas en la misma cola, `get_display_state` devuelve **todas** las llamadas activas:

```json
{
  "active_calls": [
    {"number": "A042", "desk_name": "Mesa 1", "desk_color": "#16a085"},
    {"number": "A043", "desk_name": "Mesa 2", "desk_color": "#8e44ad"}
  ]
}
```

La pantalla puede mostrar overlay al llamar/rellamar cada turno.

## Validación backend

Al llamar turno, el servidor valida:

- `desk_id` existe
- Pertenece a la misma estación
- Mesa está activa

Si `desk_id` inválido → se ignora (llamada sin mesa asignada).

## Errores frecuentes

| Síntoma | Causa real | Fix |
|---------|-----------|-----|
| Mesas creadas pero kiosco vacío | Sin colas en la estación | Crear cola en **esa** estación |
| Mesa no aparece en selector | `active=False` o sin mesas | Activar mesa |
| Dos empleados en misma mesa | Misma selección localStorage | Cada tablet elige mesa distinta |
| Mesa no llama turnos de una cola | Restricción `queue_ids` | Vaciar o añadir esa cola |

## Checklist configuración multi-mesa

```
□ 1 cola (o las que necesites) en la estación
□ N mesas con nombres claros (Mesa 1, Caja A…)
□ "Colas que atiende" vacío salvo especialización
□ Cada tablet panel con mesa distinta seleccionada
□ Pantalla TV con URL display de la misma estación
```
