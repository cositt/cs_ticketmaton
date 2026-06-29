#!/usr/bin/env python3
"""
Agente local de impresion termica para Ticketmaton.
Escucha en http://127.0.0.1:9101/print y envia bytes ESC/POS a impresora.

Uso:
  pip install pyserial  # USB/serial
  python print_agent.py --port COM3        # Windows
  python print_agent.py --port /dev/usb/lp0  # Linux
  python print_agent.py --tcp 192.168.1.100:9100  # Red

Sin dependencias (modo red TCP):
  python print_agent.py --tcp 192.168.1.100:9100
"""

import argparse
import base64
import json
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

DEFAULT_PORT = 9101


class PrintHandler(BaseHTTPRequestHandler):
    target = None

    def log_message(self, format, *args):
        print(f"[agent] {args[0]}")

    def do_POST(self):
        if self.path != "/print":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body)
            raw = base64.b64decode(payload.get("data", ""))
            if not raw:
                raise ValueError("data vacio")
            self._send_to_printer(raw)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')
        except Exception as exc:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": str(exc)}).encode())

    def _send_to_printer(self, data):
        if isinstance(PrintHandler.target, tuple):
            host, port = PrintHandler.target
            with socket.create_connection((host, port), timeout=5) as sock:
                sock.sendall(data)
        else:
            import serial
            with serial.Serial(PrintHandler.target, baudrate=9600, timeout=5) as ser:
                ser.write(data)


def main():
    parser = argparse.ArgumentParser(description="Ticketmaton print agent")
    parser.add_argument("--listen", default="127.0.0.1", help="Bind address")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="HTTP port")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--serial", dest="serial_port", help="Serial port path")
    group.add_argument("--tcp", help="Printer IP:port (raw TCP)")
    args = parser.parse_args()

    if args.tcp:
        host, _, port = args.tcp.partition(":")
        PrintHandler.target = (host, int(port or 9100))
    else:
        PrintHandler.target = args.serial_port

    server = HTTPServer((args.listen, args.port), PrintHandler)
    print(f"Ticketmaton print agent en http://{args.listen}:{args.port}/print")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDetenido.")
        sys.exit(0)


if __name__ == "__main__":
    main()
