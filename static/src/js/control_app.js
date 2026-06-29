async function jsonRpc(url, params = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params,
            id: Date.now(),
        }),
    });
    const data = await response.json();
    if (data.error) {
        throw new Error(data.error.data?.message || data.error.message || "RPC error");
    }
    return data.result;
}

function startControl(root) {
    const stationId = root.dataset.stationId;
    const token = root.dataset.token;
    const apiBase = `/ticketmaton/${stationId}/${token}`;

    root.innerHTML = `
        <div class="tc-header">
            <h1 class="tc-station-name"></h1>
            <span class="tc-status"></span>
        </div>
        <div class="tc-queues"></div>
    `;

    const queuesEl = root.querySelector(".tc-queues");
    const statusEl = root.querySelector(".tc-status");

    function flash(msg, isError = false) {
        statusEl.textContent = msg;
        statusEl.classList.toggle("tc-status-error", isError);
        clearTimeout(statusEl._t);
        statusEl._t = setTimeout(() => {
            statusEl.textContent = "";
            statusEl.classList.remove("tc-status-error");
        }, 4000);
    }

    function render(state) {
        root.querySelector(".tc-station-name").textContent = state.station_name || "";
        queuesEl.innerHTML = "";
        for (const q of state.queues || []) {
            const card = document.createElement("div");
            card.className = "tc-queue-card";
            card.style.borderTopColor = q.color || "#3498db";
            card.innerHTML = `
                <div class="tc-queue-head">
                    <h2>${q.name}</h2>
                    <span class="tc-waiting">${q.waiting_total} en espera</span>
                </div>
                <div class="tc-current">
                    <span class="tc-current-label">Atendiendo</span>
                    <span class="tc-current-number">${q.current || "—"}</span>
                </div>
                <div class="tc-next">Siguientes: ${(q.next || []).join(" · ") || "—"}</div>
                <div class="tc-actions">
                    <button class="tc-btn tc-btn-next" data-q="${q.id}">SIGUIENTE</button>
                    <button class="tc-btn tc-btn-recall" data-q="${q.id}">Rellamar</button>
                    <button class="tc-btn tc-btn-skip" data-q="${q.id}">Saltar</button>
                </div>
            `;
            queuesEl.appendChild(card);
        }
        bindButtons();
    }

    function bindButtons() {
        queuesEl.querySelectorAll(".tc-btn-next").forEach((b) =>
            b.addEventListener("click", () => doAction("call_next", b.dataset.q))
        );
        queuesEl.querySelectorAll(".tc-btn-recall").forEach((b) =>
            b.addEventListener("click", () => doAction("recall", b.dataset.q))
        );
        queuesEl.querySelectorAll(".tc-btn-skip").forEach((b) =>
            b.addEventListener("click", () => doAction("skip", b.dataset.q))
        );
    }

    async function doAction(action, queueId) {
        try {
            const result = await jsonRpc(`${apiBase}/${action}`, { queue_id: parseInt(queueId, 10) });
            if (result.error) {
                flash(result.message || "Sin turnos en espera", true);
            } else if (result.ticket) {
                flash(`Llamando ${result.ticket.number}`);
            } else if (action === "skip") {
                flash("Turno saltado");
            }
            await refresh();
        } catch (err) {
            flash(err.message, true);
        }
    }

    async function refresh() {
        try {
            const state = await jsonRpc(`${apiBase}/control_state`);
            if (!state.error) {
                render(state);
            }
        } catch (err) {
            console.error("Control refresh error:", err);
        }
    }

    refresh();
    setInterval(refresh, 3000);
}

document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("ticketmaton-control-root");
    if (root) {
        startControl(root);
    }
});

if (document.readyState !== "loading") {
    const root = document.getElementById("ticketmaton-control-root");
    if (root && !root.querySelector(".tc-header")) {
        startControl(root);
    }
}
