# -*- coding: utf-8 -*-

import uuid

from odoo import _, api, fields, models
from odoo.exceptions import UserError

TICKET_STATES = [
    ("waiting", "En espera"),
    ("calling", "Llamando"),
    ("serving", "Atendiendo"),
    ("done", "Finalizado"),
    ("skipped", "Saltado"),
    ("cancelled", "Cancelado"),
]


class TicketmatonTicket(models.Model):
    _name = "ticketmaton.ticket"
    _description = "Ticket de turno"
    _order = "create_date desc, id desc"

    station_id = fields.Many2one(
        "ticketmaton.station", required=True, ondelete="cascade", index=True
    )
    queue_id = fields.Many2one(
        "ticketmaton.queue", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(related="station_id.company_id", store=True)

    number_display = fields.Char(required=True, index=True)
    counter_value = fields.Integer(readonly=True)
    counter_segment_index = fields.Integer(readonly=True)
    access_token = fields.Char(
        default=lambda self: str(uuid.uuid4())[:12],
        required=True,
        copy=False,
        readonly=True,
    )

    state = fields.Selection(TICKET_STATES, default="waiting", required=True, index=True)
    create_date = fields.Datetime(readonly=True)
    call_date = fields.Datetime(readonly=True)
    serve_date = fields.Datetime(readonly=True)
    done_date = fields.Datetime(readonly=True)

    queue_name = fields.Char(related="queue_id.name", store=True)
    station_name = fields.Char(related="station_id.name", store=True)

    def get_public_data(self):
        self.ensure_one()
        return {
            "id": self.id,
            "number": self.number_display,
            "queue_id": self.queue_id.id,
            "queue_name": self.queue_id.name,
            "queue_color": self.queue_id.color,
            "state": self.state,
            "create_date": fields.Datetime.to_string(self.create_date),
            "call_date": fields.Datetime.to_string(self.call_date) if self.call_date else False,
            "station_id": self.station_id.id,
            "print_header": self.station_id.ticket_print_header,
            "print_width": self.station_id.ticket_print_width,
        }

    def get_print_data(self):
        """Datos para impresion termica."""
        self.ensure_one()
        station = self.station_id
        return {
            "header": station.ticket_print_header,
            "station_name": station.name,
            "queue_name": self.queue_id.name,
            "number": self.number_display,
            "date": fields.Datetime.context_timestamp(
                self, self.create_date
            ).strftime("%d/%m/%Y %H:%M"),
            "footer": station.ticket_footer,
            "width_mm": int(station.ticket_print_width),
        }

    def _notify_state(self, event="state_change"):
        for ticket in self:
            ticket.station_id._notify(event, ticket.get_public_data())

    def action_call(self):
        now = fields.Datetime.now()
        self.write({"state": "calling", "call_date": now})
        self._notify_state("ticket_calling")
        return True

    def action_serve(self):
        now = fields.Datetime.now()
        self.write({"state": "serving", "serve_date": now})
        self._notify_state("ticket_serving")
        return True

    def action_mark_done(self, silent=False):
        now = fields.Datetime.now()
        self.write({"state": "done", "done_date": now})
        if not silent:
            self._notify_state("ticket_done")
        return True

    def action_skip(self):
        self.write({"state": "skipped", "done_date": fields.Datetime.now()})
        self._notify_state("ticket_skipped")
        return True

    def action_cancel(self):
        self.write({"state": "cancelled", "done_date": fields.Datetime.now()})
        self._notify_state("ticket_cancelled")
        return True

    def action_recall(self):
        self.ensure_one()
        if self.state not in ("calling", "serving"):
            raise UserError(_("Solo se puede rellamar un turno activo."))
        self.write({"call_date": fields.Datetime.now()})
        self._notify_state("ticket_recall")
        return True

    def action_call_next_from_ticket(self):
        """Atajo: siguiente en la cola de este ticket."""
        self.ensure_one()
        return self.queue_id.action_call_next()
