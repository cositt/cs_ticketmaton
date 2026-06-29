# -*- coding: utf-8 -*-

import json
import logging
import uuid
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.urls import urljoin as url_join

_logger = logging.getLogger(__name__)

SEQUENCE_TYPES = [
    ("numeric", "Numerico (000-999)"),
    ("prefixed", "Con prefijo (A00-A99)"),
    ("multi_segment", "Multi-segmento (A00-A99, B01-B99)"),
]

RESET_POLICIES = [
    ("daily", "Reset diario"),
    ("never", "Sin reset automatico"),
    ("manual", "Solo manual"),
]

PRINT_MODES = [
    ("browser", "Navegador (window.print)"),
    ("escpos_serial", "ESC/POS Web Serial (Chrome/Edge)"),
    ("android_bridge", "Android WebView Bridge"),
    ("qz_tray", "QZ Tray (Windows)"),
    ("local_agent", "Agente local HTTP"),
    ("none", "Sin impresion"),
]


class TicketmatonStation(models.Model):
    _name = "ticketmaton.station"
    _description = "Estacion Ticketmaton"
    _order = "name, id"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    access_token = fields.Char(
        default=lambda self: str(uuid.uuid4()),
        required=True,
        copy=False,
        readonly=True,
    )

    # Mensajes personalizables
    welcome_message = fields.Char(
        default="Bienvenido", help="Titulo principal del kiosco"
    )
    subtitle_message = fields.Char(
        default="Seleccione su servicio", help="Subtitulo bajo el titulo"
    )
    ticket_header = fields.Char(
        default="Su turno es", help="Texto en pantalla tras sacar ticket"
    )
    ticket_footer = fields.Char(
        default="Espere a que se llame su numero", help="Pie del ticket en pantalla"
    )
    display_now_label = fields.Char(default="Turno actual")
    display_next_label = fields.Char(default="Siguientes")
    display_call_prefix = fields.Char(
        default="Pase a mostrador", help="Texto al llamar turno en pantalla"
    )

    # Estilo kiosco
    theme = fields.Selection(
        [("light", "Claro"), ("dark", "Oscuro")], default="light"
    )
    bg_color = fields.Char(default="#1a5276")
    button_radius = fields.Integer(default=12, help="Radio bordes botones (px)")
    button_text_size = fields.Integer(default=24, help="Tamano texto botones (px)")
    logo = fields.Image("Logo")

    # Estilo pantalla publica
    display_bg_color = fields.Char(default="#0d1b2a")
    display_text_color = fields.Char(default="#ffffff")
    display_accent_color = fields.Char(default="#e63946")
    display_font_size = fields.Integer(default=120, help="Tamano numero actual (px)")

    # Impresion
    print_mode = fields.Selection(PRINT_MODES, default="browser", required=True)
    print_agent_url = fields.Char(
        default="http://127.0.0.1:9101/print",
        help="URL del agente local de impresion (HTTP POST con ESC/POS base64)",
    )
    ticket_print_header = fields.Char(default="TICKETMATON")
    ticket_print_width = fields.Selection(
        [("58", "58mm"), ("80", "80mm")], default="58", required=True
    )
    qz_printer_name = fields.Char(help="Nombre impresora en QZ Tray")

    reset_hour = fields.Float(
        default=0.0,
        help="Hora de reset diario de contadores (0 = medianoche)",
    )

    queue_ids = fields.One2many("ticketmaton.queue", "station_id", string="Colas")
    ticket_ids = fields.One2many("ticketmaton.ticket", "station_id", string="Tickets")

    waiting_count = fields.Integer(compute="_compute_stats")
    calling_count = fields.Integer(compute="_compute_stats")
    today_ticket_count = fields.Integer(compute="_compute_stats")

    kiosk_url = fields.Char(compute="_compute_urls")
    display_url = fields.Char(compute="_compute_urls")
    control_url = fields.Char(compute="_compute_urls")

    _uniq_access_token = models.Constraint(
        "unique(access_token)",
        "El token de acceso debe ser unico",
    )

    @api.depends("access_token")
    def _compute_urls(self):
        base = self.get_base_url()
        for station in self:
            token = station.access_token
            station.kiosk_url = url_join(base, f"/ticketmaton/kiosk/{station.id}/{token}")
            station.display_url = url_join(
                base, f"/ticketmaton/display/{station.id}/{token}"
            )
            station.control_url = url_join(
                base, f"/ticketmaton/control/{station.id}/{token}"
            )

    @api.depends("ticket_ids", "ticket_ids.state")
    def _compute_stats(self):
        today_start = fields.Datetime.to_datetime(
            fields.Date.context_today(self)
        )
        for station in self:
            tickets = station.ticket_ids
            station.waiting_count = len(tickets.filtered(lambda t: t.state == "waiting"))
            station.calling_count = len(
                tickets.filtered(lambda t: t.state in ("calling", "serving"))
            )
            station.today_ticket_count = len(
                tickets.filtered(lambda t: t.create_date and t.create_date >= today_start)
            )

    def _notify(self, event_type, payload=None):
        self.ensure_one()
        self.env["bus.bus"]._sendone(
            f"ticketmaton#{self.access_token}",
            f"ticketmaton/{event_type}",
            payload or {},
        )

    def action_open_kiosk(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.kiosk_url,
            "target": "new",
        }

    def action_open_display(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.display_url,
            "target": "new",
        }

    def action_open_control(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.control_url,
            "target": "new",
        }

    def action_reset_all_queues(self):
        for station in self:
            station.queue_ids.action_reset_counter()
        return True

    def get_public_config(self):
        """Configuracion publica para kiosco y pantalla."""
        self.ensure_one()
        return {
            "id": self.id,
            "name": self.name,
            "welcome_message": self.welcome_message,
            "subtitle_message": self.subtitle_message,
            "ticket_header": self.ticket_header,
            "ticket_footer": self.ticket_footer,
            "display_now_label": self.display_now_label,
            "display_next_label": self.display_next_label,
            "display_call_prefix": self.display_call_prefix,
            "theme": self.theme,
            "bg_color": self.bg_color,
            "button_radius": self.button_radius,
            "button_text_size": self.button_text_size,
            "display_bg_color": self.display_bg_color,
            "display_text_color": self.display_text_color,
            "display_accent_color": self.display_accent_color,
            "display_font_size": self.display_font_size,
            "print_mode": self.print_mode,
            "print_agent_url": self.print_agent_url,
            "ticket_print_header": self.ticket_print_header,
            "ticket_print_width": self.ticket_print_width,
            "qz_printer_name": self.qz_printer_name or "",
            "logo": f"/ticketmaton/{self.id}/{self.access_token}/logo"
            if self.logo
            else False,
            "queues": self.queue_ids.filtered("active").get_public_data(),
        }

    def get_display_state(self):
        """Estado actual para pantalla publica."""
        self.ensure_one()
        queues_data = []
        for queue in self.queue_ids.filtered("active"):
            calling = self.env["ticketmaton.ticket"].search(
                [
                    ("queue_id", "=", queue.id),
                    ("state", "in", ("calling", "serving")),
                ],
                order="call_date desc",
                limit=1,
            )
            next_waiting = self.env["ticketmaton.ticket"].search(
                [("queue_id", "=", queue.id), ("state", "=", "waiting")],
                order="create_date asc",
                limit=3,
            )
            queues_data.append({
                "id": queue.id,
                "name": queue.name,
                "color": queue.color or "#3498db",
                "current": calling.number_display if calling else "",
                "current_id": calling.id if calling else False,
                "call_token": fields.Datetime.to_string(calling.call_date)
                if calling and calling.call_date
                else "",
                "next": [t.number_display for t in next_waiting],
            })
        return {"queues": queues_data, "station_name": self.name}

    def get_control_state(self):
        """Estado para el panel de control del empleado."""
        self.ensure_one()
        queues_data = []
        for queue in self.queue_ids.filtered("active"):
            calling = self.env["ticketmaton.ticket"].search(
                [
                    ("queue_id", "=", queue.id),
                    ("state", "in", ("calling", "serving")),
                ],
                order="call_date desc",
                limit=1,
            )
            next_waiting = self.env["ticketmaton.ticket"].search(
                [("queue_id", "=", queue.id), ("state", "=", "waiting")],
                order="create_date asc",
                limit=5,
            )
            waiting_total = self.env["ticketmaton.ticket"].search_count(
                [("queue_id", "=", queue.id), ("state", "=", "waiting")]
            )
            queues_data.append({
                "id": queue.id,
                "name": queue.name,
                "color": queue.color or "#3498db",
                "current": calling.number_display if calling else "",
                "current_id": calling.id if calling else False,
                "next": [t.number_display for t in next_waiting],
                "waiting_total": waiting_total,
            })
        return {"queues": queues_data, "station_name": self.name}
