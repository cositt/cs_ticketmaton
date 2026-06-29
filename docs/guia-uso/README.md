# Guía de uso — Ticketmaton

Documentación completa del módulo **cs_ticketmaton** para Odoo 19.

## Índice

| # | Documento | Contenido |
|---|-----------|-----------|
| 01 | [Instalación y requisitos](01-instalacion.md) | Cómo instalar, dependencias, permisos |
| 02 | [Conceptos y arquitectura](02-conceptos.md) | Estación, cola, mesa, ticket, pantallas |
| 03 | [Estaciones](03-estaciones.md) | Configuración global, URLs, reset, estadísticas |
| 04 | [Colas y numeración](04-colas-y-numeracion.md) | Tipos de numeración, reset, botones kiosco |
| 05 | [Mesas y mostradores](05-mesas-mostrador.md) | Varias mesas, misma cola, aislamiento |
| 06 | [Kiosco (cliente)](06-kiosco.md) | Pantalla táctil, sacar turno, impresión |
| 07 | [Pantalla pública (TV)](07-pantalla-publica.md) | Display, overlay, rellamada |
| 08 | [Panel empleado](08-panel-empleado.md) | Siguiente, rellamar, saltar |
| 09 | [Impresión térmica](09-impresion-termica.md) | 6 modos, agente local, Android, QZ Tray |
| 10 | [Tickets en backend](10-tickets-backend.md) | Panel Odoo, estados, filtros, acciones |
| 11 | [Personalización visual](11-personalizacion-visual.md) | Colores, mensajes, logo, temas |
| 12 | [Casos prácticos](12-casos-practicos.md) | Escenarios reales paso a paso |
| 13 | [Resolución de problemas](13-resolucion-problemas.md) | Errores frecuentes y soluciones |
| 14 | [API y URLs](14-api-urls.md) | Endpoints JSON-RPC, estructura URLs |

## Inicio rápido (5 minutos)

1. Instalar módulo → [01-instalacion.md](01-instalacion.md)
2. Crear estación con 1 cola → [03-estaciones.md](03-estaciones.md) + [04-colas-y-numeracion.md](04-colas-y-numeracion.md)
3. Abrir kiosco, pantalla y panel → [06-kiosco.md](06-kiosco.md)
4. Probar flujo: sacar turno → SIGUIENTE → ver en TV → [12-casos-practicos.md](12-casos-practicos.md)

## Resumen visual

```
                    ┌─────────────────┐
                    │    ESTACIÓN     │
                    │  (config global) │
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
      ┌─────────┐      ┌──────────┐      ┌──────────┐
      │  COLAS  │      │  MESAS   │      │ TICKETS  │
      │ (pools) │◄─────│(mostrad.)│      │ (turnos) │
      └────┬────┘      └────┬─────┘      └──────────┘
           │                │
    ┌──────┴──────┐         │
    ▼             ▼         ▼
 KIOSCO      PANTALLA    PANEL
 (cliente)    (TV)     (empleado)
```
