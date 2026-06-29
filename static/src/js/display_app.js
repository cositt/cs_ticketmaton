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
        throw new Error(data.error.data?.message || "RPC error");
    }
    return data.result;
}

function startDisplay(root) {
    const stationId = root.dataset.stationId;
    const token = root.dataset.token;
    const apiBase = `/ticketmaton/${stationId}/${token}`;

    let config = null;
    const seenCalls = {};
    let firstLoad = true;

    root.innerHTML = `
        <div class="td-header">
            <h1 class="td-station-name"></h1>
        </div>
        <div class="td-queues"></div>
        <div class="td-call-overlay d-none">
            <div class="td-call-content">
                <p class="td-call-prefix"></p>
                <div class="td-call-number"></div>
                <p class="td-call-queue"></p>
            </div>
        </div>
    `;

    const queuesEl = root.querySelector(".td-queues");
    const overlay = root.querySelector(".td-call-overlay");

    function applyConfig() {
        if (!config) return;
        root.style.setProperty("--td-bg", config.display_bg_color || "#0d1b2a");
        root.style.setProperty("--td-text", config.display_text_color || "#ffffff");
        root.style.setProperty("--td-accent", config.display_accent_color || "#e63946");
        root.style.setProperty("--td-font-size", `${config.display_font_size || 120}px`);
        root.querySelector(".td-station-name").textContent = config.name;
        root.querySelector(".td-call-prefix").textContent = config.display_call_prefix || "";
    }

    function renderQueues(state) {
        queuesEl.innerHTML = "";
        const newCalls = [];
        for (const q of state.queues || []) {
            const active = q.active_calls && q.active_calls.length
                ? q.active_calls
                : (q.current
                    ? [{ id: q.current_id, number: q.current, desk_name: "", call_token: q.call_token }]
                    : []);

            let currentHtml;
            if (!active.length) {
                currentHtml = `<div class="td-current-number">—</div>`;
            } else {
                currentHtml = active
                    .map(
                        (c) => `
                        <div class="td-current-line">
                            <span class="td-current-number">${c.number}</span>
                            ${c.desk_name ? `<span class="td-current-desk">${c.desk_name}</span>` : ""}
                        </div>`
                    )
                    .join("");
            }

            const card = document.createElement("div");
            card.className = "td-queue-card";
            card.style.borderColor = q.color || "#3498db";
            card.innerHTML = `
                <h2 class="td-queue-name">${q.name}</h2>
                <p class="td-now-label">${config?.display_now_label || "Turno actual"}</p>
                ${currentHtml}
                <p class="td-next-label">${config?.display_next_label || "Siguientes"}</p>
                <div class="td-next-numbers">${(q.next || []).join(" · ") || "—"}</div>
            `;
            queuesEl.appendChild(card);

            for (const c of active) {
                const key = `${c.id}@${c.call_token || ""}`;
                if (c.id && !seenCalls[key]) {
                    seenCalls[key] = true;
                    if (!firstLoad) {
                        newCalls.push({ number: c.number, queue: q.name, desk: c.desk_name });
                    }
                }
            }
        }
        firstLoad = false;
        if (newCalls.length) {
            // Mostrar el ultimo llamado
            const last = newCalls[newCalls.length - 1];
            showCallOverlay(last.number, last.queue, last.desk);
        }
    }

    let overlayTimer;
    function showCallOverlay(number, queueName, deskName) {
        root.querySelector(".td-call-number").textContent = number;
        const label = deskName
            ? deskName
            : queueName;
        root.querySelector(".td-call-queue").textContent = label;
        overlay.classList.remove("d-none");
        clearTimeout(overlayTimer);
        overlayTimer = setTimeout(() => overlay.classList.add("d-none"), 8000);
    }

    async function refresh() {
        try {
            const state = await jsonRpc(`${apiBase}/display_state`);
            if (!state.error) {
                renderQueues(state);
            }
        } catch (err) {
            console.error("Display refresh error:", err);
        }
    }

    async function init() {
        try {
            config = await jsonRpc(`${apiBase}/config`);
            if (config.error) {
                root.innerHTML = "<p class='text-white p-5'>Pantalla no encontrada</p>";
                return;
            }
            applyConfig();
            await refresh();
            setInterval(refresh, 1500);
        } catch (err) {
            root.innerHTML = `<p class='text-white p-5'>Error: ${err.message}</p>`;
        }
    }

    init();
}

document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("ticketmaton-display-root");
    if (root) {
        startDisplay(root);
    }
});

if (document.readyState !== "loading") {
    const root = document.getElementById("ticketmaton-display-root");
    if (root && !root.querySelector(".td-header")) {
        startDisplay(root);
    }
}
