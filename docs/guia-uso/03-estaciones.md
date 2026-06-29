# 03 — Estaciones

La **estación** es el núcleo de configuración. Todo (colas, mesas, tickets, URLs) cuelga de una estación.

## Crear estación

**Ticketmaton → Estaciones → Crear**

### Campos principales

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| Nombre | Identificador de la tienda/punto | Tienda Málaga Centro |
| Activo | Desactivar sin borrar datos | ✓ |
| Compañía | Empresa Odoo (multi-compañía) | Mi Empresa S.L. |
| Token acceso | UUID auto-generado (no editable) | `ec89da6b-6cbc-...` |

### Estadísticas (solo lectura)

| Campo | Significado |
|-------|-------------|
| En espera | Tickets con `state=waiting` |
| Llamando | Tickets en `calling` o `serving` |
| Hoy | Tickets creados hoy |

## URLs de las pantallas

Al guardar, el formulario calcula 3 URLs (campos computados):

```
Kiosco:   https://tu-dominio/ticketmaton/kiosk/1/ec89da6b-...
Pantalla: https://tu-dominio/ticketmaton/display/1/ec89da6b-...
Panel:    https://tu-dominio/ticketmaton/control/1/ec89da6b-...
```

### Botones del header

| Botón | Acción |
|-------|--------|
| Abrir Kiosco | Nueva pestaña con URL kiosco |
| Abrir Pantalla | Nueva pestaña con URL display |
| Abrir Panel Empleado | Nueva pestaña con URL control |

### Ejemplo: desplegar en tienda

```
Tablet entrada  → bookmark kiosco URL → modo pantalla completa
TV sala espera  → bookmark display URL → HDMI
Tablet mostrador → bookmark control URL → cada empleado elige mesa
```

## Pestañas del formulario

| Pestaña | Contenido |
|---------|-----------|
| Colas | Colas de turnos (inline editable) |
| Mesas / Mostradores | Puntos de atención |
| Mensajes kiosco | Textos personalizables |
| Estilo kiosco | Colores, logo, tema |
| Pantalla pública | Colores y tamaños display |
| Impresión | Modo impresora, ancho papel |
| Tickets | Historial de turnos de esta estación |

## Reset de contadores

### Reset diario automático

Cada cola con política **Reset diario** reinicia su contador cuando:

1. Cambia la fecha (respecto a `last_reset_date`)
2. La hora actual ≥ `reset_hour` de la estación

| Campo estación | Valor | Efecto |
|----------------|-------|--------|
| Hora reset | `0.0` | Medianoche (00:00) |
| Hora reset | `8.5` | 08:30 cada día |

### Reset manual

**Botón "Resetear contadores"** en el formulario de estación → llama `action_reset_all_queues()` en todas las colas.

Útil al inicio de jornada o tras pruebas.

### Ejemplo: tienda que abre a las 9:00

```
Estación → Hora reset: 9.0
Cola Atención → Reset: Diario
```

A las 9:00 del día siguiente, la numeración vuelve al mínimo configurado.

## Seguridad del token

- El `access_token` es un UUID único por estación
- Sin token válido → HTTP 404 en todas las rutas
- No compartir el token públicamente si quieres restringir acceso
- Para rotar token: contactar desarrollo (campo readonly; requiere acción técnica)

## Multi-estación

Cada tienda = una estación independiente:

```
Estación "Málaga"     → colas propias, mesas propias, URLs propias
Estación "Sevilla"    → colas propias, mesas propias, URLs propias
```

**No** se comparten colas entre estaciones. Si creas mesas en estación 2 pero las colas están en estación 1, el kiosco de estación 2 no tendrá botones.

## Ejemplo completo: nueva tienda

```
1. Crear estación "Farmacia Norte"
2. Mensaje bienvenida: "Bienvenido a Farmacia Norte"
3. Subtítulo: "Pulse para sacar turno"
4. Pestaña Colas → añadir "Atención" (ver cap. 04)
5. Pestaña Mesas → añadir "Mostrador 1", "Mostrador 2"
6. Guardar → copiar URLs a dispositivos
7. Probar kiosco: debe mostrar botón "Atención"
```
