/**
 * Mini Project: Online Complaint Management System
 * Client-Side JavaScript (Authentication, Guards & Grievance Actions)
 */

// -------------------------------------------------------------
// 1. Authentication Handlers (Login, Register, Logout)
// -------------------------------------------------------------

// Student Login Form
const studentLoginForm = document.getElementById("studentLoginForm");
if (studentLoginForm) {
    studentLoginForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const btn = document.getElementById("studentLoginBtn");
        const msg = document.getElementById("authMessage");
        btn.disabled = true;
        btn.innerText = "Signing in...";

        const payload = {
            role: "student",
            identifier: document.getElementById("login_identifier").value.trim(),
            password: document.getElementById("login_password").value
        };

        try {
            const res = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (res.ok && data.success) {
                msg.className = "message-box success";
                msg.innerText = "✅ Login successful! Redirecting to Student Portal...";
                setTimeout(() => { window.location.href = "student.html"; }, 800);
            } else {
                throw new Error(data.message || "Invalid credentials.");
            }
        } catch (err) {
            msg.className = "message-box error";
            msg.innerText = `❌ ${err.message}`;
            btn.disabled = false;
            btn.innerText = "Sign In to Student Portal";
        }
    });
}

// Student Registration Form
const studentRegisterForm = document.getElementById("studentRegisterForm");
if (studentRegisterForm) {
    studentRegisterForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const btn = document.getElementById("studentRegisterBtn");
        const msg = document.getElementById("authMessage");

        const pwd = document.getElementById("reg_password").value;
        const confirmPwd = document.getElementById("reg_confirm_password").value;

        if (pwd !== confirmPwd) {
            msg.className = "message-box error";
            msg.innerText = "❌ Passwords do not match. Please re-enter.";
            return;
        }

        if (pwd.length < 6) {
            msg.className = "message-box error";
            msg.innerText = "❌ Password must be at least 6 characters long.";
            return;
        }

        btn.disabled = true;
        btn.innerText = "Creating account...";

        const payload = {
            full_name: document.getElementById("reg_fullname").value.trim(),
            student_id: document.getElementById("reg_student_id").value.trim(),
            email: document.getElementById("reg_email").value.trim(),
            password: pwd
        };

        try {
            const res = await fetch("/api/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (res.ok && data.success) {
                msg.className = "message-box success";
                msg.innerText = "🎉 Account registered successfully! Please login below.";
                studentRegisterForm.reset();
                setTimeout(() => {
                    switchAuthTab("student-login");
                    document.getElementById("login_identifier").value = payload.email;
                }, 1200);
            } else {
                throw new Error(data.message || "Registration failed.");
            }
        } catch (err) {
            msg.className = "message-box error";
            msg.innerText = `❌ ${err.message}`;
        } finally {
            btn.disabled = false;
            btn.innerText = "Register Account";
        }
    });
}

// Admin Login Form
const adminLoginForm = document.getElementById("adminLoginForm");
if (adminLoginForm) {
    adminLoginForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const btn = document.getElementById("adminLoginBtn");
        const msg = document.getElementById("authMessage");
        btn.disabled = true;
        btn.innerText = "Authenticating...";

        const payload = {
            role: "admin",
            identifier: document.getElementById("admin_email").value.trim(),
            password: document.getElementById("admin_password").value
        };

        try {
            const res = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (res.ok && data.success) {
                msg.className = "message-box success";
                msg.innerText = "✅ Admin authenticated! Opening Console...";
                setTimeout(() => { window.location.href = "admin.html"; }, 800);
            } else {
                throw new Error(data.message || "Invalid administrator credentials.");
            }
        } catch (err) {
            msg.className = "message-box error";
            msg.innerText = `❌ ${err.message}`;
            btn.disabled = false;
            btn.innerText = "Sign In to Admin Console";
        }
    });
}

// Logout Handler
async function handleLogout() {
    try {
        await fetch("/api/logout", { method: "POST" });
    } catch (e) {
        // ignore network error
    }
    window.location.href = "index.html";
}

// -------------------------------------------------------------
// 2. Student Portal Page Initialization & Logic
// -------------------------------------------------------------
let currentStudent = null;

async function initStudentPage() {
    try {
        const res = await fetch("/api/me");
        const user = await res.json();

        if (!res.ok || !user.logged_in || user.role !== "student") {
            window.location.href = "index.html";
            return;
        }

        currentStudent = user;

        // Populate badges and form
        const userBadge = document.getElementById("studentUserBadge");
        if (userBadge) {
            userBadge.innerText = `👤 ${user.name} (${user.student_id})`;
        }

        const heading = document.getElementById("welcomeHeading");
        if (heading) {
            heading.innerText = `Welcome, ${user.name}`;
        }

        const nameInput = document.getElementById("c_student_name");
        const idInput = document.getElementById("c_student_id");
        if (nameInput) nameInput.value = user.name;
        if (idInput) idInput.value = user.student_id;

        loadStudentComplaints();
    } catch (err) {
        window.location.href = "index.html";
    }
}

// Student submits complaint
const studentComplaintForm = document.getElementById("studentComplaintForm");
if (studentComplaintForm) {
    studentComplaintForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const btn = document.getElementById("studentSubmitBtn");
        const msg = document.getElementById("studentFormMessage");
        btn.disabled = true;
        btn.innerText = "Submitting...";

        const payload = {
            student_name: currentStudent ? currentStudent.name : document.getElementById("c_student_name").value,
            student_id: currentStudent ? currentStudent.student_id : document.getElementById("c_student_id").value,
            category: document.getElementById("c_category").value,
            title: document.getElementById("c_title").value.trim(),
            description: document.getElementById("c_description").value.trim()
        };

        try {
            const res = await fetch("/api/complaints", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (res.ok && data.success) {
                msg.className = "message-box success";
                msg.innerText = `✅ Grievance submitted successfully! Reference ID: #${data.id}`;
                document.getElementById("c_title").value = "";
                document.getElementById("c_description").value = "";
                document.getElementById("c_category").selectedIndex = 0;
                loadStudentComplaints();
            } else {
                throw new Error(data.message || "Failed to submit.");
            }
        } catch (err) {
            msg.className = "message-box error";
            msg.innerText = `❌ Error: ${err.message}`;
        } finally {
            btn.disabled = false;
            btn.innerText = "Submit Complaint";
            setTimeout(() => { msg.style.display = "none"; }, 6000);
        }
    });
}

// Load complaints for this student
async function loadStudentComplaints() {
    const tableBody = document.getElementById("studentComplaintsTableBody");
    if (!tableBody) return;

    tableBody.innerHTML = `<tr><td colspan="5" class="text-center" style="padding:2rem;">Loading your complaints...</td></tr>`;

    try {
        const res = await fetch("/api/complaints");
        const data = await res.json();

        if (!res.ok) throw new Error(data.message || "Could not fetch records");

        if (!data || data.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center" style="padding:2.5rem; color:#64748b;">You haven't submitted any complaints yet.</td></tr>`;
            return;
        }

        tableBody.innerHTML = data.map(c => `
            <tr>
                <td><strong>#${c.id}</strong></td>
                <td><span style="font-weight:700; color:#334155;">${escapeHtml(c.category)}</span></td>
                <td>
                    <div style="font-weight:700; color:#0f172a;">${escapeHtml(c.title)}</div>
                    <div style="font-size:0.85rem; color:#475569; margin-top:0.25rem;">${escapeHtml(c.description)}</div>
                </td>
                <td>${getStatusBadge(c.status)}</td>
                <td style="font-size:0.85rem; color:#64748b;">${formatDate(c.created_at)}</td>
            </tr>
        `).join("");
    } catch (err) {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center" style="color:#ef4444;">Error: ${err.message}</td></tr>`;
    }
}

// -------------------------------------------------------------
// 3. Admin Console Page Initialization & Logic
// -------------------------------------------------------------
let allAdminComplaints = [];

async function initAdminPage() {
    try {
        const res = await fetch("/api/me");
        const user = await res.json();

        if (!res.ok || !user.logged_in || user.role !== "admin") {
            window.location.href = "index.html";
            return;
        }

        const badge = document.getElementById("adminUserBadge");
        if (badge) {
            badge.innerText = `🛡️ Admin: ${user.name} (${user.email})`;
        }

        loadAdminComplaints();
    } catch (err) {
        window.location.href = "index.html";
    }
}

async function loadAdminComplaints() {
    const tableBody = document.getElementById("adminTableBody");
    if (!tableBody) return;

    tableBody.innerHTML = `<tr><td colspan="7" class="text-center" style="padding:2rem;">Loading complaints registry...</td></tr>`;

    try {
        const res = await fetch("/api/complaints");
        const data = await res.json();

        if (!res.ok) throw new Error(data.message || "Failed to load complaints");

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
        tableBody.innerHTML = `<tr><td colspan="7" class="text-center" style="padding:2.5rem; color:#64748b;">No complaints found matching criteria.</td></tr>`;
        return;
    }

    tableBody.innerHTML = data.map(c => `
        <tr>
            <td><strong>#${c.id}</strong></td>
            <td>
                <strong>${escapeHtml(c.student_name)}</strong>
                <div style="font-size:0.8rem; color:#64748b;">${escapeHtml(c.student_id)}</div>
            </td>
            <td><span style="font-weight:700; color:#334155;">${escapeHtml(c.category)}</span></td>
            <td>
                <div style="font-weight:700; color:#0f172a;">${escapeHtml(c.title)}</div>
                <div style="font-size:0.85rem; color:#475569; margin-top:0.2rem;">${escapeHtml(c.description)}</div>
            </td>
            <td>${getStatusBadge(c.status)}</td>
            <td>
                <select onchange="updateStatus(${c.id}, this.value)" style="padding:0.35rem 0.5rem; font-size:0.85rem; font-weight:600; border-radius:6px;">
                    <option value="Pending" ${c.status === "Pending" ? "selected" : ""}>Pending</option>
                    <option value="In Progress" ${c.status === "In Progress" ? "selected" : ""}>In Progress</option>
                    <option value="Resolved" ${c.status === "Resolved" ? "selected" : ""}>Resolved</option>
                </select>
            </td>
            <td class="text-center">
                <button class="btn btn-sm btn-danger" onclick="deleteComplaint(${c.id})" title="Delete Complaint">
                    🗑️
                </button>
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

async function updateStatus(id, newStatus) {
    try {
        const res = await fetch(`/api/complaints/${id}/status`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await res.json();
        if (res.ok && data.success) {
            loadAdminComplaints();
        } else {
            alert(`Failed to update status: ${data.message || 'Error'}`);
            loadAdminComplaints();
        }
    } catch (err) {
        alert(`Error updating status: ${err.message}`);
        loadAdminComplaints();
    }
}

async function deleteComplaint(id) {
    if (!confirm(`Are you sure you want to permanently delete complaint #${id}?`)) return;

    try {
        const res = await fetch(`/api/complaints/${id}`, { method: "DELETE" });
        const data = await res.json();
        if (res.ok && data.success) {
            loadAdminComplaints();
        } else {
            alert(`Failed to delete: ${data.message}`);
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
