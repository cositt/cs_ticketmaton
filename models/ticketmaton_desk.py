# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TicketmatonDesk(models.Model):
    _name = "ticketmaton.desk"
    _description = "Mesa / Mostrador de atencion"
    _order = "sequence, id"

    name = fields.Char(required=True, help="Ej: Mesa 1, Mostrador 2, Caja A")
    station_id = fields.Many2one(
        "ticketmaton.station", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="station_id.company_id", store=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    color = fields.Char(default="#16a085", help="Color de la mesa en pantalla")

    # Colas que puede atender esta mesa; vacio = todas las de la estacion
    queue_ids = fields.Many2many(
        "ticketmaton.queue",
        string="Colas que atiende",
        help="Vacio = atiende todas las colas de la estacion",
    )

    def get_public_data(self):
        return [
            {
                "id": d.id,
                "name": d.name,
                "color": d.color or "#16a085",
                "queue_ids": d.queue_ids.ids,
            }
            for d in self
        ]
