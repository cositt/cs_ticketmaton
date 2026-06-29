# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from odoo.tools import consteq
from odoo.tools.image import image_data_uri


class TicketmatonController(http.Controller):

    def _get_station(self, station_id, token):
        station = request.env["ticketmaton.station"].sudo().browse(int(station_id))
        if not station.exists() or not consteq(station.access_token, token):
            return request.env["ticketmaton.station"]
        return station

    # ---- KIOSCO ----

    @http.route(
        "/ticketmaton/kiosk/<int:station_id>/<string:token>",
        type="http",
        auth="public",
        website=True,
    )
    def kiosk(self, station_id, token, **kwargs):
        station = self._get_station(station_id, token)
        if not station:
            return request.not_found()
        return request.render("cs_ticketmaton.kiosk_page", {
            "station": station,
            "token": token,
        })

    # ---- PANTALLA PUBLICA ----

    @http.route(
        "/ticketmaton/display/<int:station_id>/<string:token>",
        type="http",
        auth="public",
        website=True,
    )
    def display(self, station_id, token, **kwargs):
        station = self._get_station(station_id, token)
        if not station:
            return request.not_found()
        return request.render("cs_ticketmaton.display_page", {
            "station": station,
            "token": token,
        })

    # ---- PANEL EMPLEADO ----

    @http.route(
        "/ticketmaton/control/<int:station_id>/<string:token>",
        type="http",
        auth="public",
        website=True,
    )
    def control(self, station_id, token, **kwargs):
        station = self._get_station(station_id, token)
        if not station:
            return request.not_found()
        return request.render("cs_ticketmaton.control_page", {
            "station": station,
            "token": token,
        })

    @http.route(
        "/ticketmaton/<int:station_id>/<string:token>/control_state",
        type="jsonrpc",
        auth="public",
    )
    def get_control_state(self, station_id, token):
        station = self._get_station(station_id, token)
        if not station:
            return {"error": "not_found"}
        return station.get_control_state()

    @http.route(
        "/ticketmaton/<int:station_id>/<string:token>/call_next",
        type="jsonrpc",
        auth="public",
    )
    def call_next(self, station_id, token, queue_id, desk_id=None):
        station = self._get_station(station_id, token)
        if not station:
            return {"error": "not_found"}
        queue = request.env["ticketmaton.queue"].sudo().browse(int(queue_id))
        if not queue.exists() or queue.station_id.id != station.id:
            return {"error": "invalid_queue"}
        desk_id = self._valid_desk(station, desk_id)
        try:
            ticket = queue.action_call_next(desk_id=desk_id)
        except Exception as exc:
            return {"error": "no_waiting", "message": str(exc)}
        return {"ticket": ticket.get_public_data()}

    @http.route(
        "/ticketmaton/<int:station_id>/<string:token>/recall",
        type="jsonrpc",
        auth="public",
    )
    def recall(self, station_id, token, queue_id, desk_id=None):
        station = self._get_station(station_id, token)
        if not station:
            return {"error": "not_found"}
        queue = request.env["ticketmaton.queue"].sudo().browse(int(queue_id))
        if not queue.exists() or queue.station_id.id != station.id:
            return {"error": "invalid_queue"}
        desk_id = self._valid_desk(station, desk_id)
        try:
            ticket = queue.action_recall_current(desk_id=desk_id)
        except Exception as exc:
            return {"error": "no_active", "message": str(exc)}
        return {"ticket": ticket.get_public_data()}

    @http.route(
        "/ticketmaton/<int:station_id>/<string:token>/skip",
        type="jsonrpc",
        auth="public",
    )
    def skip(self, station_id, token, queue_id, desk_id=None):
        station = self._get_station(station_id, token)
        if not station:
            return {"error": "not_found"}
        queue = request.env["ticketmaton.queue"].sudo().browse(int(queue_id))
        if not queue.exists() or queue.station_id.id != station.id:
            return {"error": "invalid_queue"}
        desk_id = self._valid_desk(station, desk_id)
        skip_domain = [
            ("queue_id", "=", queue.id),
            ("state", "in", ("calling", "serving")),
        ]
        if desk_id:
            skip_domain.append(("desk_id", "=", desk_id))
        current = request.env["ticketmaton.ticket"].sudo().search(
            skip_domain, order="call_date desc", limit=1
        )
        if current:
            current.action_skip()
        try:
            ticket = queue.action_call_next(desk_id=desk_id)
        except Exception:
            return {"skipped": bool(current), "ticket": False}
        return {"skipped": bool(current), "ticket": ticket.get_public_data()}

    def _valid_desk(self, station, desk_id):
        if not desk_id:
            return None
        desk = request.env["ticketmaton.desk"].sudo().browse(int(desk_id))
        if desk.exists() and desk.station_id.id == station.id and desk.active:
            return desk.id
        return None

    # ---- LOGO ----

    @http.route(
        "/ticketmaton/<int:station_id>/<string:token>/logo",
        type="http",
        auth="public",
    )
    def station_logo(self, station_id, token):
        station = self._get_station(station_id, token)
        if not station or not station.logo:
            return request.not_found()
        return request.env["ir.binary"]._get_image_stream_from(
            station, "logo"
        ).get_response()

    # ---- API JSON-RPC ----

    @http.route(
        "/ticketmaton/<int:station_id>/<string:token>/config",
        type="jsonrpc",
        auth="public",
    )
    def get_config(self, station_id, token):
        station = self._get_station(station_id, token)
        if not station:
            return {"error": "not_found"}
        return station.get_public_config()

    @http.route(
        "/ticketmaton/<int:station_id>/<string:token>/display_state",
        type="jsonrpc",
        auth="public",
    )
    def get_display_state(self, station_id, token):
        station = self._get_station(station_id, token)
        if not station:
            return {"error": "not_found"}
        return station.get_display_state()

    @http.route(
        "/ticketmaton/<int:station_id>/<string:token>/take_ticket",
        type="jsonrpc",
        auth="public",
    )
    def take_ticket(self, station_id, token, queue_id):
        station = self._get_station(station_id, token)
        if not station:
            return {"error": "not_found"}
        queue = request.env["ticketmaton.queue"].sudo().browse(int(queue_id))
        if not queue.exists() or queue.station_id.id != station.id or not queue.active:
            return {"error": "invalid_queue"}
        try:
            ticket = queue.create_ticket()
        except Exception as exc:
            return {"error": "create_failed", "message": str(exc)}
        return {
            "ticket": ticket.get_public_data(),
            "print_data": ticket.get_print_data(),
        }

    @http.route(
        "/ticketmaton/<int:station_id>/<string:token>/bus_channel",
        type="jsonrpc",
        auth="public",
    )
    def get_bus_channel(self, station_id, token):
        station = self._get_station(station_id, token)
        if not station:
            return {"error": "not_found"}
        return {"channel": f"ticketmaton#{station.access_token}"}
