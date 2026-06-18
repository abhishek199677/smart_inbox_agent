const API_BASE = "http://localhost:8000/api/v1";

document.addEventListener("DOMContentLoaded", () => {
    loadTickets();
});

function submitTask() {
    const task = document.getElementById("task-input").value.trim();
    if (!task) {
        alert("Please enter a support request.");
        return;
    }

    const btn = document.getElementById("submit-btn");
    btn.disabled = true;
    btn.textContent = "Processing...";

    fetch(`${API_BASE}/agent/process`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task }),
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result-category").textContent = data.category;
        document.getElementById("result-session").textContent = data.session_id;
        document.getElementById("result-response").textContent = data.final_response;
        document.getElementById("result-summary").textContent = data.summary;
        document.getElementById("result-section").style.display = "block";
        document.getElementById("task-input").value = "";
        loadTickets();
    })
    .catch(err => {
        alert("Error: " + err.message);
    })
    .finally(() => {
        btn.disabled = false;
        btn.textContent = "Process with AI Agent";
    });
}

function loadTickets() {
    const filter = document.getElementById("category-filter").value;
    const url = filter
        ? `${API_BASE}/tickets?category=${encodeURIComponent(filter)}`
        : `${API_BASE}/tickets`;

    fetch(url)
        .then(res => res.json())
        .then(data => {
            const tickets = data.tickets || [];
            const tbody = document.getElementById("tickets-body");
            tbody.innerHTML = tickets.map(t => `
                <tr>
                    <td><code>${t.session_id.slice(0, 8)}...</code></td>
                    <td>${t.task.slice(0, 60)}${t.task.length > 60 ? "..." : ""}</td>
                    <td>${t.category}</td>
                    <td>${t.status}</td>
                    <td>${new Date(t.created_at).toLocaleString()}</td>
                </tr>
            `).join("");
        })
        .catch(err => console.error("Failed to load tickets:", err));

    fetch(`${API_BASE}/stats`)
        .then(res => res.json())
        .then(stats => {
            const bar = document.getElementById("stats-bar");
            const catStr = Object.entries(stats.categories || {})
                .map(([k, v]) => `${k}: ${v}`)
                .join(" | ");
            bar.innerHTML = `Total: ${stats.total_tickets} ${catStr ? " | " + catStr : ""}`;
        })
        .catch(() => {});
}
