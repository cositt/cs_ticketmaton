# 11 — Personalización visual

Todo configurable desde Odoo sin tocar código.

## Mensajes kiosco (estación)

| Campo | Pantalla | Ejemplo |
|-------|----------|---------|
| welcome_message | Título grande | Bienvenido |
| subtitle_message | Subtítulo | Seleccione su servicio |
| ticket_header | Tras sacar turno | Su turno es |
| ticket_footer | Pie en kiosco e impresión | Espere a que se llame su número |

### Ejemplo tienda infantil

```
welcome_message:   ¡Hola! Bienvenido a Pequeño Planeta
subtitle_message:  ¿En qué podemos ayudarte?
ticket_header:     Tu número es
ticket_footer:     Te llamaremos por pantalla. ¡Gracias!
```

## Estilo kiosco (estación)

| Campo | Efecto | Ejemplo |
|-------|--------|---------|
| theme | Claro / Oscuro | dark |
| bg_color | Color fondo | #1a5276 |
| button_radius | Redondeo botones (px) | 16 |
| button_text_size | Tamaño texto botones (px) | 28 |
| logo | Imagen cabecera | PNG 200x80 |

### Ejemplo tema oscuro

```
theme:             dark
bg_color:          #0d1117
button_radius:     20
button_text_size:  32
```

Logo se sirve en `/ticketmaton/<id>/<token>/logo`.

## Estilo por cola (botones kiosco)

En cada línea de cola:

| Campo | Ejemplo cola Atención | Ejemplo cola Recogida |
|-------|----------------------|----------------------|
| button_label | Atención personalizada | Recoger pedido |
| button_color | #2980b9 | #27ae60 |
| button_text_color | #ffffff | #ffffff |
| button_icon | fa-user | fa-shopping-bag |
| color | #3498db | #e67e22 |

Iconos Font Awesome 4: `fa-ticket`, `fa-heart`, `fa-truck`, etc.

## Pantalla pública (estación)

| Campo | Efecto | Valor ejemplo |
|-------|--------|---------------|
| display_now_label | Etiqueta turno actual | Ahora atiende |
| display_next_label | Etiqueta cola espera | Próximos turnos |
| display_call_prefix | Texto overlay | Diríjase a |
| display_bg_color | Fondo TV | #0d1b2a |
| display_text_color | Texto | #ffffff |
| display_accent_color | Overlay / acentos | #e63946 |
| display_font_size | Tamaño número (px) | 150 |

### Ejemplo pantalla alto contraste

```
display_bg_color:      #000000
display_text_color:    #ffffff
display_accent_color:  #ffff00
display_font_size:     180
display_call_prefix:   ATENCIÓN — Pase a
```

## Color mesa

En cada mesa, campo **Color** → aparece en overlay TV junto al nombre de mesa.

```
Mesa 1 → #16a085 (verde)
Mesa 2 → #8e44ad (morado)
```

## Impresión (textos)

| Campo | Dónde aparece |
|-------|---------------|
| ticket_print_header | Cabecera papel |
| ticket_footer | Pie papel (mismo que kiosco) |

## Checklist branding completo

```
□ Logo subido en estación
□ Colores corporativos en bg_color y botones
□ Mensajes en tono de marca
□ display_accent_color alineado con identidad
□ Probar en kiosco real (táctil + legibilidad)
□ Probar en TV a distancia (tamaño display_font_size)
```

## Lo que NO es configurable (sin desarrollo)

- Layout HTML de las 3 pantallas
- Fuentes tipográficas custom
- Sonido de llamada (no implementado)
- Vídeos / publicidad en pantalla
- PIN en panel empleado
