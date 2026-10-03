/**
 * Mini Project: Online Complaint Management System
 * Client-Side JavaScript (Fetch API & DOM Updates)
 */

const API_BASE = "/api/complaints";

// -------------------------------------------------------------
// 1. Student Complaint Submission
// -------------------------------------------------------------
const complaintForm = document.getElementById("complaintForm");
if (complaintForm) {
    complaintForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        
        const submitBtn = document.getElementById("submitBtn");
        const msgBox = document.getElementById("formMessage");
        
        submitBtn.disabled = true;
        submitBtn.innerText = "Submitting...";

        const payload = {
            student_name: document.getElementById("student_name").value.trim(),
            student_id: document.getElementById("student_id").value.trim(),
            category: document.getElementById("category").value,
            title: document.getElementById("title").value.trim(),
            description: document.getElementById("description").value.trim()
        };

        try {
            const res = await fetch(API_BASE, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();

            if (res.ok && data.success) {
                msgBox.className = "message-box success";
                msgBox.innerText = `✅ Complaint submitted successfully! (Reference ID: #${data.id || data.complaint_id || 'NEW'})`;
                complaintForm.reset();
                loadComplaints();
            } else {
                throw new Error(data.message || "Failed to submit complaint.");
            }
        } catch (err) {
            msgBox.className = "message-box error";
            msgBox.innerText = `❌ Error: ${err.message}`;
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerText = "Submit Complaint";
            setTimeout(() => { msgBox.style.display = "none"; }, 6000);
        }
    });

    // Auto-load on page ready
    document.addEventListener("DOMContentLoaded", loadComplaints);
}

// -------------------------------------------------------------
// 2. Load Student Complaints List
// -------------------------------------------------------------
async function loadComplaints() {
    const tableBody = document.getElementById("complaintsTableBody");
    if (!tableBody) return;

    tableBody.innerHTML = `<tr><td colspan="6" class="text-center">Loading complaints...</td></tr>`;

    try {
        const res = await fetch(API_BASE);
        const data = await res.json();

        if (!res.ok) throw new Error(data.message || "Failed to fetch complaints");

        if (!data || data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="6" class="text-center">No complaints submitted yet.</td></tr>`;
            return;
        }

        tableBody.innerHTML = data.map(c => `
            <tr>
                <td><strong>#${c.id}</strong></td>
                <td>
                    <strong>${escapeHtml(c.student_name)}</strong>
                    <div style="font-size:0.8rem; color:#64748b;">${escapeHtml(c.student_id)}</div>
                </td>
                <td><span style="font-weight:600; color:#475569;">${escapeHtml(c.category)}</span></td>
                <td>
                    <strong>${escapeHtml(c.title)}</strong>
                    <div style="font-size:0.85rem; color:#475569; margin-top:0.2rem;">${escapeHtml(c.description)}</div>
                </td>
                <td>${getStatusBadge(c.status)}</td>
                <td style="font-size:0.85rem; color:#64748b;">${formatDate(c.created_at)}</td>
            </tr>
        `).join("");
    } catch (err) {
        tableBody.innerHTML = `<tr><td colspan="6" class="text-center" style="color:#ef4444;">Error loading complaints: ${err.message}</td></tr>`;
    }
}

// -------------------------------------------------------------
// 3. Admin: Load Complaints & Summary Statistics
// -------------------------------------------------------------
let allAdminComplaints = [];

async function loadAdminComplaints() {
    const tableBody = document.getElementById("adminTableBody");
    if (!tableBody) return;

    tableBody.innerHTML = `<tr><td colspan="7" class="text-center">Loading admin data...</td></tr>`;

    try {
        const res = await fetch(API_BASE);
        const data = await res.json();

        if (!res.ok) throw new Error(data.message || "Failed to load admin records");

        allAdminComplaints = data || [];
        updateAdminKPIs(allAdminComplaints);
        renderAdminTable(allAdminComplaints);
    } catch (err) {
        tableBody.innerHTML = `<tr><td colspan="7" class="text-center" style="color:#ef4444;">Error loading complaints: ${err.message}</td></tr>`;
    }
}

function updateAdminKPIs(data) {
    const total = data.length;
    const pending = data.filter(c => c.status === "Pending").length;
    const progress = data.filter(c => c.status === "In Progress").length;
    const resolved = data.filter(c => c.status === "Resolved").length;

    const elTotal = document.getElementById("statTotal");
    const elPending = document.getElementById("statPending");
    const elProgress = document.getElementById("statProgress");
    const elResolved = document.getElementById("statResolved");

    if (elTotal) elTotal.innerText = total;
    if (elPending) elPending.innerText = pending;
    if (elProgress) elProgress.innerText = progress;
    if (elResolved) elResolved.innerText = resolved;
}

function renderAdminTable(data) {
    const tableBody = document.getElementById("adminTableBody");
    if (!tableBody) return;

    if (data.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="7" class="text-center">No complaints match criteria.</td></tr>`;
        return;
    }

    tableBody.innerHTML = data.map(c => `
        <tr>
            <td><strong>#${c.id}</strong></td>
            <td>
                <strong>${escapeHtml(c.student_name)}</strong>
                <div style="font-size:0.8rem; color:#64748b;">${escapeHtml(c.student_id)}</div>
            </td>
            <td><span style="font-weight:600; color:#475569;">${escapeHtml(c.category)}</span></td>
            <td>
                <strong>${escapeHtml(c.title)}</strong>
                <div style="font-size:0.85rem; color:#475569;">${escapeHtml(c.description)}</div>
            </td>
            <td>${getStatusBadge(c.status)}</td>
            <td>
                <select class="btn-sm" onchange="updateStatus(${c.id}, this.value)" style="padding:0.35rem 0.5rem; border-radius:5px; border:1px solid #cbd5e1;">
                    <option value="Pending" ${c.status === "Pending" ? "selected" : ""}>Pending</option>
                    <option value="In Progress" ${c.status === "In Progress" ? "selected" : ""}>In Progress</option>
                    <option value="Resolved" ${c.status === "Resolved" ? "selected" : ""}>Resolved</option>
                </select>
            </td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="deleteComplaint(${c.id})">🗑️ Delete</button>
            </td>
        </tr>
    `).join("");
}

function filterAdminComplaints() {
    const filter = document.getElementById("statusFilter").value;
    if (filter === "All") {
        renderAdminTable(allAdminComplaints);
    } else {
        const filtered = allAdminComplaints.filter(c => c.status === filter);
        renderAdminTable(filtered);
    }
}

// -------------------------------------------------------------
// 4. Update Complaint Status (Admin)
// -------------------------------------------------------------
async function updateStatus(id, newStatus) {
    try {
        const res = await fetch(`${API_BASE}/${id}/status`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await res.json();
        if (res.ok && data.success) {
            loadAdminComplaints();
        } else {
            alert(`Failed to update status: ${data.message || 'Unknown error'}`);
            loadAdminComplaints();
        }
    } catch (err) {
        alert(`Error updating status: ${err.message}`);
        loadAdminComplaints();
    }
}

// -------------------------------------------------------------
// 5. Delete Complaint (Admin)
// -------------------------------------------------------------
async function deleteComplaint(id) {
    if (!confirm(`Are you sure you want to delete complaint #${id}?`)) return;

    try {
        const res = await fetch(`${API_BASE}/${id}`, {
            method: "DELETE"
        });
        const data = await res.json();
        if (res.ok && data.success) {
            loadAdminComplaints();
        } else {
            alert(`Failed to delete complaint: ${data.message}`);
        }
    } catch (err) {
        alert(`Error deleting complaint: ${err.message}`);
    }
}

// -------------------------------------------------------------
// Helper Utilities
// -------------------------------------------------------------
function getStatusBadge(status) {
    const s = (status || "").toLowerCase();
    if (s.includes("pending")) return `<span class="badge badge-pending">Pending</span>`;
    if (s.includes("progress")) return `<span class="badge badge-in-progress">In Progress</span>`;
    if (s.includes("resolved")) return `<span class="badge badge-resolved">Resolved</span>`;
    return `<span class="badge" style="background:#e2e8f0; color:#334155;">${escapeHtml(status)}</span>`;
}

function escapeHtml(text) {
    if (!text) return "";
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatDate(dateStr) {
    if (!dateStr) return "-";
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    } catch (e) {
        return dateStr.substring(0, 10);
    }
}
