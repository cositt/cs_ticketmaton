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

function startKiosk(root) {
    const stationId = root.dataset.stationId;
    const token = root.dataset.token;
    const apiBase = `/ticketmaton/${stationId}/${token}`;

    let config = null;
    let printer = null;
    let screen = "home";

    root.innerHTML = `
        <div class="tk-screen tk-home">
            <div class="tk-logo-wrap"></div>
            <h1 class="tk-welcome"></h1>
            <p class="tk-subtitle"></p>
            <div class="tk-buttons"></div>
        </div>
        <div class="tk-screen tk-ticket d-none">
            <div class="tk-ticket-card">
                <p class="tk-ticket-header"></p>
                <div class="tk-ticket-number"></div>
                <p class="tk-ticket-queue"></p>
                <p class="tk-ticket-footer"></p>
            </div>
            <button type="button" class="btn btn-lg tk-btn-back">Nuevo turno</button>
        </div>
        <div class="tk-loading d-none">
            <div class="spinner-border text-light" role="status"></div>
        </div>
    `;

    const homeEl = root.querySelector(".tk-home");
    const ticketEl = root.querySelector(".tk-ticket");
    const loadingEl = root.querySelector(".tk-loading");
    const buttonsEl = root.querySelector(".tk-buttons");

    function showScreen(name) {
        screen = name;
        homeEl.classList.toggle("d-none", name !== "home");
        ticketEl.classList.toggle("d-none", name !== "ticket");
    }

    function setLoading(on) {
        loadingEl.classList.toggle("d-none", !on);
    }

    function applyStyles() {
        if (!config) return;
        root.style.setProperty("--tk-bg", config.bg_color || "#1a5276");
        root.style.setProperty("--tk-btn-radius", `${config.button_radius || 12}px`);
        root.style.setProperty("--tk-btn-size", `${config.button_text_size || 24}px`);
        root.classList.toggle("tk-dark", config.theme === "dark");

        root.querySelector(".tk-welcome").textContent = config.welcome_message;
        root.querySelector(".tk-subtitle").textContent = config.subtitle_message;
        root.querySelector(".tk-ticket-header").textContent = config.ticket_header;
        root.querySelector(".tk-ticket-footer").textContent = config.ticket_footer;

        const logoWrap = root.querySelector(".tk-logo-wrap");
        if (config.logo) {
            logoWrap.innerHTML = `<img src="${config.logo}" alt="logo" class="tk-logo"/>`;
        } else {
            logoWrap.innerHTML = "";
        }

        buttonsEl.innerHTML = "";
        for (const queue of config.queues || []) {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "tk-queue-btn";
            btn.style.backgroundColor = queue.button_color || "#2980b9";
            btn.style.color = queue.button_text_color || "#ffffff";
            btn.innerHTML = `<i class="fa ${queue.button_icon || "fa-ticket"}"></i><span>${queue.button_label}</span>`;
            btn.addEventListener("click", () => takeTicket(queue.id));
            buttonsEl.appendChild(btn);
        }
    }

    async function takeTicket(queueId) {
        setLoading(true);
        try {
            const result = await jsonRpc(`${apiBase}/take_ticket`, { queue_id: queueId });
            if (result.error) {
                alert(result.message || "Error al crear turno");
                return;
            }
            const { ticket, print_data: printData } = result;
            root.querySelector(".tk-ticket-number").textContent = ticket.number;
            root.querySelector(".tk-ticket-queue").textContent = ticket.queue_name;
            showScreen("ticket");

            if (printer && printData) {
                await printer.print(printData);
            }
        } catch (err) {
            console.error(err);
            alert("Error de conexion");
        } finally {
            setLoading(false);
        }
    }

    root.querySelector(".tk-btn-back").addEventListener("click", () => showScreen("home"));

    let inactivityTimer;
    function resetInactivity() {
        clearTimeout(inactivityTimer);
        if (screen === "ticket") {
            inactivityTimer = setTimeout(() => showScreen("home"), 30000);
        }
    }
    root.addEventListener("click", resetInactivity);

    async function init() {
        try {
            config = await jsonRpc(`${apiBase}/config`);
            if (config.error) {
                root.innerHTML = "<p class='text-danger p-5'>Estacion no encontrada</p>";
                return;
            }
            printer = new window.TicketmatonPrinter(config);
            applyStyles();
        } catch (err) {
            root.innerHTML = `<p class='text-danger p-5'>Error: ${err.message}</p>`;
        }
    }

    init();
}

document.addEventListener("DOMContentLoaded", () => {
    const root = document.getElementById("ticketmaton-kiosk-root");
    if (root) {
        startKiosk(root);
    }
});

// Si el modulo carga tarde (assets lazy), arrancar igual
if (document.readyState !== "loading") {
    const root = document.getElementById("ticketmaton-kiosk-root");
    if (root && !root.querySelector(".tk-home")) {
        startKiosk(root);
    }
}
