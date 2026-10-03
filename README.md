# Online Complaint Management System (College Mini Project)

A clean, lightweight, and modern college mini-project built with **HTML5**, **CSS3**, **JavaScript**, **Python (Flask)**, and **MySQL** (with SQLite auto-fallback).

---

## 📁 Project Structure (Only Essential Files)

```text
ONLINE COMPLAINT MANAGEMENT SYSTEM/
├── index.html            # Authentication Gateway (Student Sign In, Sign Up, Forgot Password, Admin Login)
├── student.html          # Protected Student Dashboard (Submit Complaints, Live Status Tracker)
├── admin.html            # Protected Admin Console (KPI Cards, Status Updater, Complaint Management)
├── style.css             # Modern, high-contrast, responsive styling
├── script.js             # Client-side dynamic logic, auth guards, and API integrations
├── app.py                # Lightweight Python Flask REST API server with session security & OTP reset
├── database.sql          # MySQL database schema & sample data (ready for phpMyAdmin import)
├── complaint_db.sqlite   # Pre-seeded local SQLite database (for plug-and-play local execution)
├── requirements.txt      # Python dependencies (flask, mysql-connector-python)
├── vercel.json           # Vercel serverless deployment routing config
├── api/
│   └── index.py          # Vercel WSGI entry point
└── README.md             # Project documentation & setup instructions
```

---

## 🎯 Key Features

1. **Authentication Hub (`index.html`)**:
   - **Student Login**: Sign in with registered Email or Student Roll Number + Password.
   - **Student Sign Up**: Self-registration for new students with encrypted passwords.
   - **Forgot Password via Email OTP**: 2-step password reset with 6-digit OTP verification.
   - **Admin Login**: Secure administrative login with 1-click demo autofill button.

2. **Student Dashboard (`student.html`)**:
   - Auto-filled Name and Roll Number.
   - Grievance submission form categorized into Classroom, Lab, Hostel, Wi-Fi, Library, etc.
   - Real-time personal complaints table with color-coded status badges (*Pending*, *In Progress*, *Resolved*).
   - Session logout.

3. **Admin Console (`admin.html`)**:
   - Summary metric cards (Total Complaints, Pending, In Progress, Resolved).
   - Filter complaints by status.
   - 1-click status updater dropdown.
   - Delete complaint records.
   - Session logout.

4. **Dual Database Engine**:
   - Connects to **MySQL** automatically if running.
   - Automatically falls back to **SQLite** if MySQL is offline, so it never crashes!

---

## 💻 How to Run Locally

1. Open PowerShell or Command Prompt in this folder:
   ```powershell
   cd "C:\Users\Vaiz\OneDrive\Desktop\ONLINE COMPLAINT MANAGEMENT SYSTEM"
   ```
2. Start the application:
   ```powershell
   python app.py
   ```
3. Open your browser:
   👉 **http://127.0.0.1:5000**

### 🔑 Test Credentials
- **Student**: `rahul.sharma@college.com` (or Roll `CS101`) | Password: `Student@123`
- **Admin**: `admin@college.com` | Password: `Admin@123` *(or click the ⚡ autofill button on the Admin tab)*

---

## 🚀 How to Deploy on Vercel via GitHub

### Step 1: Push to GitHub
1. Create a new empty repository on [GitHub](https://github.com/new) named `college-complaint-system`.
2. In this folder, run:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/college-complaint-system.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Vercel
1. Log in to [vercel.com](https://vercel.com) and click **"Add New..." ➔ "Project"**.
2. Select your `college-complaint-system` repository and click **Import**.
3. Keep default settings (Framework: *Other*) and click **Deploy**.
4. Your system will be live on a free `https://your-project.vercel.app` URL in under 60 seconds!
