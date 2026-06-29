# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from .ticketmaton_station import RESET_POLICIES, SEQUENCE_TYPES

_logger = logging.getLogger(__name__)


class TicketmatonQueue(models.Model):
    _name = "ticketmaton.queue"
    _description = "Cola de turnos"
    _order = "sequence, id"

    name = fields.Char(required=True)
    code = fields.Char(required=True, help="Codigo corto interno, ej: ATN, CAJ")
    station_id = fields.Many2one(
        "ticketmaton.station", required=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="station_id.company_id", store=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    # Boton kiosco
    button_label = fields.Char(help="Texto boton; vacio = nombre cola")
    button_color = fields.Char(default="#2980b9")
    button_text_color = fields.Char(default="#ffffff")
    button_icon = fields.Char(default="fa-ticket", help="Clase FontAwesome")

    # Numeracion
    sequence_type = fields.Selection(SEQUENCE_TYPES, default="numeric", required=True)
    prefix = fields.Char(default="", help="Prefijo fijo para tipo prefixed")
    padding = fields.Integer(default=3, help="Digitos de relleno")
    min_value = fields.Integer(default=0)
    max_value = fields.Integer(default=999)
    multi_segment_rules = fields.Text(
        default='[{"prefix": "A", "min": 0, "max": 99, "padding": 2}, {"prefix": "B", "min": 1, "max": 99, "padding": 2}]',
        help="JSON array de segmentos para multi_segment",
    )
    reset_policy = fields.Selection(RESET_POLICIES, default="daily", required=True)
    last_reset_date = fields.Date(readonly=True)

    # Contador interno (bloqueado en transaccion al crear ticket)
    counter_value = fields.Integer(default=-1, readonly=True)
    counter_segment_index = fields.Integer(default=0, readonly=True)

    color = fields.Char(default="#3498db", help="Color en pantalla publica")
    ticket_ids = fields.One2many("ticketmaton.ticket", "queue_id")

    waiting_count = fields.Integer(compute="_compute_waiting_count")

    _uniq_code_per_station = models.Constraint(
        "unique(station_id, code)",
        "El codigo de cola debe ser unico por estacion",
    )

    @api.depends("ticket_ids.state")
    def _compute_waiting_count(self):
        for queue in self:
            queue.waiting_count = len(
                queue.ticket_ids.filtered(lambda t: t.state == "waiting")
            )

    @api.constrains("padding", "min_value", "max_value")
    def _check_values(self):
        for queue in self:
            if queue.padding < 1 or queue.padding > 6:
                raise ValidationError(_("El padding debe estar entre 1 y 6."))
            if queue.min_value > queue.max_value:
                raise ValidationError(_("El valor minimo no puede superar el maximo."))

    def _parse_segments(self):
        self.ensure_one()
        if self.sequence_type != "multi_segment":
            return []
        try:
            segments = json.loads(self.multi_segment_rules or "[]")
        except json.JSONDecodeError as exc:
            raise UserError(_("Reglas multi-segmento JSON invalidas: %s") % exc) from exc
        if not segments:
            raise UserError(_("Debe definir al menos un segmento."))
        return segments

    def _maybe_reset_counter(self):
        """Reset diario si aplica."""
        self.ensure_one()
        if self.reset_policy != "daily":
            return
        today = fields.Date.context_today(self)
        if not self.last_reset_date:
            self.last_reset_date = today
            return
        if self.last_reset_date == today:
            return
        station = self.station_id
        reset_hour = int(station.reset_hour or 0)
        now = fields.Datetime.now()
        if now.hour >= reset_hour:
            self.write({
                "counter_value": self.min_value - 1,
                "counter_segment_index": 0,
                "last_reset_date": today,
            })

    def _format_number(self, value, prefix="", padding=None):
        padding = padding or self.padding
        if prefix:
            return f"{prefix}{value:0{padding}d}"
        return f"{value:0{padding}d}"

    def _next_number_display(self):
        """Calcula siguiente numero SIN incrementar (preview)."""
        self.ensure_one()
        self._maybe_reset_counter()

        if self.sequence_type == "numeric":
            next_val = self.counter_value + 1
            if next_val > self.max_value:
                if self.reset_policy == "daily":
                    next_val = self.min_value
                else:
                    raise UserError(
                        _("Cola %(name)s agotada (max %(max)s).", name=self.name, max=self.max_value)
                    )
            return self._format_number(next_val), next_val, 0

        if self.sequence_type == "prefixed":
            next_val = self.counter_value + 1
            if next_val > self.max_value:
                if self.reset_policy == "daily":
                    next_val = self.min_value
                else:
                    raise UserError(_("Cola %(name)s agotada.", name=self.name))
            return self._format_number(next_val, self.prefix), next_val, 0

        # multi_segment
        segments = self._parse_segments()
        seg_idx = min(self.counter_segment_index, len(segments) - 1)
        seg = segments[seg_idx]
        seg_min = seg.get("min", 0)
        seg_max = seg.get("max", 99)
        seg_pad = seg.get("padding", 2)
        seg_prefix = seg.get("prefix", "")

        next_val = self.counter_value + 1 if self.counter_value >= seg_min else seg_min
        next_seg_idx = seg_idx

        if next_val > seg_max:
            next_seg_idx = seg_idx + 1
            if next_seg_idx >= len(segments):
                if self.reset_policy == "daily":
                    next_seg_idx = 0
                    next_val = segments[0].get("min", 0)
                else:
                    raise UserError(_("Cola %(name)s: todos los segmentos agotados.", name=self.name))
            else:
                next_val = segments[next_seg_idx].get("min", 0)
                seg_prefix = segments[next_seg_idx].get("prefix", "")
                seg_pad = segments[next_seg_idx].get("padding", 2)

        display = self._format_number(next_val, seg_prefix, seg_pad)
        return display, next_val, next_seg_idx

    def _increment_counter(self, value, segment_index):
        self.ensure_one()
        self.write({
            "counter_value": value,
            "counter_segment_index": segment_index,
        })

    def action_reset_counter(self):
        for queue in self:
            queue.write({
                "counter_value": queue.min_value - 1,
                "counter_segment_index": 0,
                "last_reset_date": fields.Date.context_today(queue),
            })
        return True

    def action_call_next(self):
        """Llama al siguiente ticket en espera."""
        self.ensure_one()
        ticket = self.env["ticketmaton.ticket"].search(
            [("queue_id", "=", self.id), ("state", "=", "waiting")],
            order="create_date asc",
            limit=1,
        )
        if not ticket:
            raise UserError(_("No hay turnos en espera en %(name)s.", name=self.name))

        # Marcar anteriores en calling/serving como done
        old_active = self.env["ticketmaton.ticket"].search([
            ("queue_id", "=", self.id),
            ("state", "in", ("calling", "serving")),
        ])
        old_active.action_mark_done(silent=True)

        ticket.action_call()
        return ticket

    def action_recall_current(self):
        """Rellama el turno actual."""
        self.ensure_one()
        ticket = self.env["ticketmaton.ticket"].search(
            [("queue_id", "=", self.id), ("state", "in", ("calling", "serving"))],
            order="call_date desc",
            limit=1,
        )
        if not ticket:
            raise UserError(_("No hay turno activo para rellamar."))
        ticket.action_recall()
        return ticket

    def get_public_data(self):
        return [
            {
                "id": q.id,
                "name": q.name,
                "code": q.code,
                "button_label": q.button_label or q.name,
                "button_color": q.button_color,
                "button_text_color": q.button_text_color,
                "button_icon": q.button_icon,
                "color": q.color,
            }
            for q in self
        ]

    def create_ticket(self):
        """Crea ticket con bloqueo de fila para evitar duplicados."""
        self.ensure_one()
        self.env.cr.execute(
            "SELECT id FROM ticketmaton_queue WHERE id = %s FOR UPDATE",
            [self.id],
        )
        display, value, seg_idx = self._next_number_display()
        ticket = self.env["ticketmaton.ticket"].create({
            "station_id": self.station_id.id,
            "queue_id": self.id,
            "number_display": display,
            "counter_value": value,
            "counter_segment_index": seg_idx,
            "state": "waiting",
        })
        self._increment_counter(value, seg_idx)
        self.station_id._notify("ticket_created", ticket.get_public_data())
        return ticket
