/**
 * Servicio de impresion multi-plataforma.
 *
 * Modos soportados:
 * - browser: window.print con CSS termico
 * - escpos_serial: Web Serial API (Chrome/Edge Windows/Android)
 * - android_bridge: window.TicketmatonAndroid.printEscPos(base64)
 * - qz_tray: QZ Tray en Windows
 * - local_agent: HTTP POST a agente local
 * - none: sin impresion
 */
class TicketPrinter {
    constructor(config) {
        this.config = config;
        this._serialPort = null;
    }

    async print(printData) {
        const mode = this.config.print_mode || "browser";
        switch (mode) {
            case "none":
                return { ok: true, mode: "none" };
            case "escpos_serial":
                return this._printEscPosSerial(printData);
            case "android_bridge":
                return this._printAndroidBridge(printData);
            case "qz_tray":
                return this._printQzTray(printData);
            case "local_agent":
                return this._printLocalAgent(printData);
            case "browser":
            default:
                return this._printBrowser(printData);
        }
    }

    _buildEscPos(printData) {
        const width = parseInt(printData.width_mm || this.config.ticket_print_width || 58, 10);
        const builder = new window.TicketmatonEscPosBuilder(width);
        return builder.buildTicket(printData);
    }

    async _printEscPosSerial(printData) {
        if (!navigator.serial) {
            console.warn("Web Serial no disponible, fallback a browser print");
            return this._printBrowser(printData);
        }
        try {
            if (!this._serialPort) {
                this._serialPort = await navigator.serial.requestPort();
                await this._serialPort.open({ baudRate: 9600 });
            }
            const data = this._buildEscPos(printData);
            const writer = this._serialPort.writable.getWriter();
            await writer.write(data);
            writer.releaseLock();
            return { ok: true, mode: "escpos_serial" };
        } catch (err) {
            console.error("ESC/POS Serial error:", err);
            return this._printBrowser(printData);
        }
    }

    async _printAndroidBridge(printData) {
        const bridge =
            window.TicketmatonAndroid ||
            window.AndroidBridge ||
            (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.ticketmaton);
        if (!bridge) {
            console.warn("Android bridge no encontrado, fallback browser");
            return this._printBrowser(printData);
        }
        const builder = new window.TicketmatonEscPosBuilder(parseInt(printData.width_mm || 58, 10));
        builder.buildTicket(printData);
        const base64 = builder.toBase64();
        try {
            if (typeof bridge.printEscPos === "function") {
                bridge.printEscPos(base64);
            } else if (typeof bridge.postMessage === "function") {
                bridge.postMessage({ action: "print", data: base64 });
            } else {
                window.location.href = `ticketmaton://print?data=${encodeURIComponent(base64)}`;
            }
            return { ok: true, mode: "android_bridge" };
        } catch (err) {
            console.error("Android bridge error:", err);
            return this._printBrowser(printData);
        }
    }

    async _printQzTray(printData) {
        if (typeof window.qz === "undefined") {
            console.warn("QZ Tray no cargado, fallback browser");
            return this._printBrowser(printData);
        }
        const builder = new window.TicketmatonEscPosBuilder(parseInt(printData.width_mm || 58, 10));
        builder.buildTicket(printData);
        const base64 = builder.toBase64();
        const printer = this.config.qz_printer_name || null;
        try {
            if (!window.qz.websocket.isActive()) {
                await window.qz.websocket.connect();
            }
            const config = qz.configs.create(printer);
            await qz.print(config, [{
                type: "raw",
                format: "base64",
                data: base64,
            }]);
            return { ok: true, mode: "qz_tray" };
        } catch (err) {
            console.error("QZ Tray error:", err);
            return this._printBrowser(printData);
        }
    }

    async _printLocalAgent(printData) {
        const url = this.config.print_agent_url || "http://127.0.0.1:9101/print";
        const builder = new window.TicketmatonEscPosBuilder(parseInt(printData.width_mm || 58, 10));
        builder.buildTicket(printData);
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    data: builder.toBase64(),
                    format: "escpos_base64",
                }),
            });
            if (!response.ok) {
                throw new Error(`Agent HTTP ${response.status}`);
            }
            return { ok: true, mode: "local_agent" };
        } catch (err) {
            console.error("Local agent error:", err);
            return this._printBrowser(printData);
        }
    }

    _printBrowser(printData) {
        return new Promise((resolve) => {
            const existing = document.getElementById("ticketmaton-print-area");
            if (existing) {
                existing.remove();
            }
            const area = document.createElement("div");
            area.id = "ticketmaton-print-area";
            area.className = "ticketmaton-print-area";
            area.innerHTML = `
                <div class="ticketmaton-print-ticket">
                    <div class="print-header">${this._esc(printData.header)}</div>
                    <div class="print-station">${this._esc(printData.station_name)}</div>
                    <div class="print-queue">${this._esc(printData.queue_name)}</div>
                    <div class="print-number">${this._esc(printData.number)}</div>
                    <div class="print-date">${this._esc(printData.date)}</div>
                    <div class="print-footer">${this._esc(printData.footer)}</div>
                </div>
            `;
            document.body.appendChild(area);
            window.print();
            setTimeout(() => {
                area.remove();
                resolve({ ok: true, mode: "browser" });
            }, 500);
        });
    }

    _esc(str) {
        const div = document.createElement("div");
        div.textContent = str || "";
        return div.innerHTML;
    }
}

window.TicketmatonPrinter = TicketPrinter;
