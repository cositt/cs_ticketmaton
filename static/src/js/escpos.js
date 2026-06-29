/**
 * Generador ESC/POS para impresoras termicas.
 * Compatible con la mayoria de impresoras 58mm y 80mm.
 */
class EscPosBuilder {
    constructor(widthMm = 58) {
        this.charsPerLine = widthMm >= 80 ? 48 : 32;
        this.buffer = [];
    }

    _bytes(...values) {
        this.buffer.push(...values);
        return this;
    }

    _text(str) {
        const encoder = new TextEncoder();
        this.buffer.push(...encoder.encode(str));
        return this;
    }

    init() {
        return this._bytes(0x1b, 0x40);
    }

    alignCenter() {
        return this._bytes(0x1b, 0x61, 0x01);
    }

    alignLeft() {
        return this._bytes(0x1b, 0x61, 0x00);
    }

    bold(on = true) {
        return this._bytes(0x1b, 0x45, on ? 0x01 : 0x00);
    }

    doubleHeight(on = true) {
        return this._bytes(0x1d, 0x21, on ? 0x11 : 0x00);
    }

    line(text = "") {
        const trimmed = text.substring(0, this.charsPerLine);
        this._text(trimmed + "\n");
        return this;
    }

    separator(char = "-") {
        return this.line(char.repeat(this.charsPerLine));
    }

    feed(lines = 3) {
        return this._bytes(0x1b, 0x64, lines);
    }

    cut() {
        return this._bytes(0x1d, 0x56, 0x00);
    }

    buildTicket(printData) {
        this.init()
            .alignCenter()
            .bold(true)
            .line(printData.header || "TICKETMATON")
            .bold(false)
            .line(printData.station_name || "")
            .separator()
            .alignCenter()
            .line(printData.queue_name || "")
            .doubleHeight(true)
            .bold(true)
            .line(printData.number || "")
            .doubleHeight(false)
            .bold(false)
            .separator()
            .line(printData.date || "")
            .feed(1)
            .alignCenter()
            .line(printData.footer || "")
            .feed(3)
            .cut();
        return new Uint8Array(this.buffer);
    }

    toBase64() {
        const bytes = new Uint8Array(this.buffer);
        let binary = "";
        for (const b of bytes) {
            binary += String.fromCharCode(b);
        }
        return btoa(binary);
    }
}

window.TicketmatonEscPosBuilder = EscPosBuilder;
