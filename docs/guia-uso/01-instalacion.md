# 01 — Instalación y requisitos

## Requisitos

| Requisito | Detalle |
|-----------|---------|
| Odoo | 19.0 |
| Módulos Odoo | `base`, `web`, `bus`, `website` |
| Navegador kiosco | Chrome o Edge recomendado (impresión Web Serial) |
| Hardware opcional | Tablet kiosco, TV, impresora térmica 58/80mm |

## Instalación

### 1. Copiar el módulo

Colocar `cs_ticketmaton` en la ruta de addons de Odoo (ej. `/mnt/custom`).

### 2. Actualizar lista de aplicaciones

**Aplicaciones → Actualizar lista de aplicaciones** (modo desarrollador activo).

### 3. Instalar

Buscar **Ticketmaton - Sistema de Turnos** → **Instalar**.

### 4. Verificar menú

Debe aparecer **Ticketmaton** en el menú principal con:

- Panel
- Estaciones (solo administradores)
- Colas (solo administradores)

## Permisos

| Grupo | Permisos |
|-------|----------|
| **Ticketmaton / Usuario** | Ver estaciones, colas; gestionar tickets (llamar, finalizar) |
| **Ticketmaton / Administrador** | Todo lo anterior + crear/editar estaciones, colas, mesas |

Asignar en **Ajustes → Usuarios → [usuario] → Derechos de acceso → Ticketmaton**.

### Ejemplo: empleado de mostrador

```
Usuario: maria@tienda.com
Grupo: Ticketmaton / Usuario
```

Puede usar el panel web y el menú Panel en Odoo. No puede modificar configuración de estaciones.

### Ejemplo: responsable de tienda

```
Usuario: jefe@tienda.com
Grupo: Ticketmaton / Administrador
```

Puede crear estaciones, colas, mesas y resetear contadores.

## Actualizar el módulo

Tras cambios en código:

```bash
docker exec odoo19_runtime odoo -c /etc/odoo/odoo.conf -d odoo -u cs_ticketmaton --stop-after-init
docker restart odoo19_runtime
```

O desde Odoo: **Aplicaciones → Ticketmaton → Actualizar**.

## Datos demo

Al instalar se crea la estación demo **Bebe Malaga - Tienda** con:

- Cola "Atención" (prefijo A, 3 dígitos)
- Cola "Recogida" (numérico 000-999)

Puedes usarla para pruebas o archivarla y crear la tuya.
