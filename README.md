# 🏛️ Online Complaint Management System

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

[![MySQL](https://img.shields.io/badge/MySQL-TiDB%20Cloud-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)

[![SQLite](https://img.shields.io/badge/SQLite-Fallback%20Engine-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)

> A modern, responsive, and secure full-stack campus grievance
> management portal designed for educational institutions. Facilitates
> end-to-end complaint tracking from student submission with optional
> photo evidence to administrative resolution workflows.

------------------------------------------------------------------------

## 🌐 Live Demo & Repository

-   **Live Application:**
    <https://online-complaint-management-system-pied.vercel.app/>

-   **GitHub Repository:**
    <https://github.com/ShaikhVaiz/online-complaint-management-system>

------------------------------------------------------------------------

## 📑 Table of Contents

-   [Project Overview](#-project-overview)

-   [Problem Statement](#-problem-statement)

-   [Key Features](#-key-features)

-   [Application Workflow](#-application-workflow)

-   [System Architecture](#-system-architecture)

-   [Technology Stack](#-technology-stack)

-   [Project Folder Structure](#-project-folder-structure)

-   [Database Design](#-database-design)

-   [Local Installation & Setup](#-local-installation--setup)

-   [Environment Variables](#-environment-variables)

-   [Running the Application](#-running-the-application)

-   [Running Automated Tests](#-running-automated-tests)

-   [Deployment Guide](#-deployment-guide)

-   [Recommended Screenshots](#-recommended-screenshots)

-   [Future Improvements](#-future-improvements)

-   [Author](#-author)

------------------------------------------------------------------------

## 📖 Project Overview

The **Online Complaint Management System** is an institutional grievance
redressal platform engineered to replace inefficient manual complaint
registers and unorganized email threads with a centralized web portal.

The application serves two user roles:

1.  **Students**: Register securely, log in using their email address or
    college roll number, lodge categorized grievances with optional
    compressed photo evidence, recover forgotten passwords via email OTP
    verification, and track the status of their submitted complaints in
    real time.

2.  **Administrators**: Access an authenticated dashboard featuring
    campus grievance metrics, filter complaints by status, review
    complaint details and attached evidence on demand, update complaint
    resolution states (`Pending`, `In Progress`, `Resolved`), and
    maintain institutional accountability.

------------------------------------------------------------------------

## 🎯 Problem Statement

Traditional campus grievance handling mechanisms suffer from multiple
friction points:

-   **Lack of Tracking & Transparency**: Students submitting paper forms
    or informal verbal complaints have no record of whether their
    concern was logged, investigated, or resolved.

-   **Administrative Overload**: Campus facility teams receive
    fragmented complaints across multiple channels without
    categorization, timestamps, or priority sorting.

-   **Slow Resolution & Poor Evidence**: Text-only descriptions often
    lack crucial context (such as broken equipment photos or exact room
    locations), resulting in back-and-forth communication delays.

-   **Accountability Gaps**: Absence of an auditable status workflow
    makes it difficult to measure resolution times and institutional
    performance.

This system addresses these challenges by offering a structured,
transparent, and mobile-responsive digital grievance pipeline.

------------------------------------------------------------------------

## 🚀 Key Features

### 1. Student Registration & Dual Identifier Login

-   **Self-Registration**: New students register with their full name,
    unique student ID / roll number, email address, and password.

-   **Validation**: Enforces required fields, minimum password length (6
    characters), password matching, and duplicate checks for email and
    roll numbers.

-   **Flexible Login Identifier**: Students can authenticate using
    either their registered **email address** or their **roll number /
    student ID**.

-   **Cryptographic Security**: Passwords are securely hashed using
    Werkzeug (`generate_password_hash`) using modern key derivation
    functions.

### 2. Email OTP Password Recovery

-   **Two-Step Verification**: Students initiate password resets by
    entering their registered email.

-   **One-Time Password (OTP)**: Generates a cryptographically secure
    6-digit OTP code stored with a 10-minute expiration window.

-   **Multi-Provider Dispatch**:

    -   Primary: [Resend](https://resend.com) REST API with
        authenticated domain delivery.

    -   Secondary: Standard Gmail / custom SMTP relay.

    -   Tertiary: [Brevo](https://www.brevo.com) (formerly Sendinblue)
        transactional email API.

-   **Tamper Protection**: Verifies OTP against signed session tokens
    and the database reset table before updating the hashed student
    password.

### 3. Student Dashboard & Grievance Lodging

-   **Personalized Portal**: Authenticated session displays student name
    and roll number.

-   **Categorized Grievance Form**: Supports campus categories including
    **Classroom**, **Laboratory**, **Hostel**, **Wi-Fi / Internet**,
    **Library**, **Sports**, **Transport**, and **Other**.

-   **Optional Photo Attachment & Removal**:

    -   Students can optionally attach photo evidence (JPG, PNG, WebP).

    -   Client-side Canvas preprocessing resizes oversized images down
        to a maximum dimension of 900px, reducing memory overhead and
        upload bandwidth.

    -   Includes a dedicated `❌ Remove Image` button to clear
        attachments before submission.

-   **Deterministic Sequential Complaint IDs**: Grievances are assigned
    sequential, user-friendly complaint numbers starting from `#1`
    (`#1, #2, #3, ...`).

### 4. Personal Complaint Tracking

-   **Scoped Data Access**: Students can only access and view their own
    lodged complaints.

-   **Status Badges**: Visual high-contrast badges for complaint states:

    -   \<span style="color:#92400e; background:#fef3c7; padding:2px
        8px; border-radius:4px; font-weight:bold;"\>Pending\</span\> -
        Submitted and awaiting review.

    -   \<span style="color:#1e40af; background:#dbeafe; padding:2px
        8px; border-radius:4px; font-weight:bold;"\>In
        Progress\</span\> - Under investigation / assigned to
        technician.

    -   \<span style="color:#14532d; background:#dcfce7; padding:2px
        8px; border-radius:4px; font-weight:bold;"\>Resolved\</span\> -
        Issue addressed and resolved.

-   **Modal Evidence Viewer**: Clicking `📷 View Image` opens a
    responsive modal dialog with in-memory caching for swift
    re-inspection.

### 5. Administrator Dashboard & Management Console

-   **Role-Based Protection**: Administrator console routes
    (`admin.html` and administrative APIs) are guarded by session
    authentication.

-   **Real-Time KPI Metric Cards**: Live counters calculate total campus
    grievances, pending tickets, active investigations, and resolved
    issues.

-   **Status Filter**: Instant client-side filtering by resolution state
    (`All`, `Pending`, `In Progress`, `Resolved`).

-   **Inline Status Workflow**: Administrators can update ticket status
    via an inline dropdown that immediately updates the backend
    database.

-   **Record Deletion**: Permanent record removal with administrative
    confirmation guards.

### 6. Performance Optimization & Lazy Image Loading

-   **Lightweight List Payload**: The `/api/complaints` listing endpoint
    queries metadata and a boolean `has_image` flag, deliberately
    omitting heavy Base64 image strings from the initial table fetch.

-   **On-Demand Evidence Fetching**: Complaint images are loaded only
    when an administrator or student clicks `📷 View Photo` /
    `📷 View Image`, requesting the dedicated
    `/api/complaints/\<id>/image` endpoint.

-   **Client Caching**: Once fetched, evidence is stored in memory
    (`complaintPhotosMap`), eliminating redundant network round trips on
    repeat views.

-   **Database Indexing**: Indexed on `complaint_no` and `student_id`
    for efficient filtering and ordering.

### 7. Dual Database Engine (Cloud MySQL + SQLite Fallback)

-   **Primary Engine**: Connects to Cloud MySQL (such as TiDB Cloud
    Serverless or AWS RDS) with automated SSL certificate discovery via
    `certifi`.

-   **Auto-Fallback Engine**: If remote MySQL is unreachable, the system
    automatically transitions to an embedded SQLite database
    (`complaint_db.sqlite`), preventing server downtime in local or
    disconnected environments.

------------------------------------------------------------------------

## 🔄 Application Workflow

``` mermaid

sequenceDiagram

    autonumber

    actor Student

    actor Admin

    participant Frontend as Browser UI (script.js)

    participant Backend as Flask API (app.py)

    participant Database as Database (MySQL / SQLite)

    %% Student Complaint Lodging

    Student->>Frontend: Fill Grievance & attach optional image

    Frontend->>Frontend: Client Canvas resizes image to max 900px

    Frontend->>Backend: POST /api/complaints (JSON payload)

    Backend->>Database: INSERT INTO complaints with sequential complaint_no

    Database-->>Backend: Return new complaint_no

    Backend-->>Frontend: 200 OK (id: next_no, message: success)

    Frontend->>Student: Display success banner with #ID

    %% Admin Triage & Lazy Load

    Admin->>Frontend: Open Admin Dashboard

    Frontend->>Backend: GET /api/complaints

    Backend->>Database: SELECT metadata + has_image (omits Base64)

    Database-->>Backend: Complaint records

    Backend-->>Frontend: Lightweight JSON (images omitted)

    Frontend->>Admin: Render table & live KPI counters

    %% On-Demand Photo Viewer

    Admin->>Frontend: Click "📷 View Photo" on Complaint #ID

    alt Image cached in memory

        Frontend->>Admin: Instantly render modal viewer

    else Not cached

        Frontend->>Backend: GET /api/complaints/\<id>/image

        Backend->>Database: SELECT image_data WHERE complaint_no = id

        Database-->>Backend: Base64 image payload

        Backend-->>Frontend: Return image_data

        Frontend->>Frontend: Cache in complaintPhotosMap

        Frontend->>Admin: Display full-size photo in modal

    end

    %% Status Update

    Admin->>Frontend: Change status dropdown to "Resolved"

    Frontend->>Backend: PUT /api/complaints/\<id>/status {"status": "Resolved"}

    Backend->>Database: UPDATE complaints SET status = 'Resolved'

    Database-->>Backend: Updated

    Backend-->>Frontend: 200 OK (Status updated)

    Frontend->>Admin: Update KPI counters & badge state
```

------------------------------------------------------------------------

## 🏗️ System Architecture

``` mermaid

flowchart TD

    subgraph Client["Client Tier (Vanilla JS, HTML5, CSS3)"]

        A1["index.html\<br/>(Student Login, Sign Up, Admin Login, OTP Reset)"]

        A2["student.html\<br/>(Complaint Form & Personal Tracker)"]

        A3["admin.html\<br/>(Admin Triage Console & KPI Counters)"]

        A4["script.js\<br/>(Auth Guards, Canvas Resizer, Modal Viewer, API Handlers)"]

        A5["style.css\<br/>(High-Contrast Responsive UI)"]

    end

    subgraph Server["Application Tier (Python Flask)"]

        B1["app.py\<br/>(REST API, Session Auth, Werkzeug Security)"]

        B2["api/index.py\<br/>(Vercel Serverless WSGI Adapter)"]

        B3["Email Dispatcher\<br/>(Resend API / SMTP / Brevo API)"]

    end

    subgraph Storage["Data Tier (Dual Engine)"]

        C1[("Cloud MySQL / TiDB Serverless\<br/>(Primary with SSL CA Auto-Discovery)")]

        C2[("SQLite Database\<br/>(Automatic Fallback Engine)")]

    end

    Client -->|HTTPS REST JSON| Server

    B1 -->|Primary Connection| C1

    B1 -.->|Automatic Fallback| C2

    B1 -->|HTTP API / SMTP| B3
```

------------------------------------------------------------------------

## 💻 Technology Stack

| Layer \| Technology \| Purpose \|

\|---\|---\|---\|

| **Frontend** \| **HTML5** \| Semantic, accessible layout structure for
  authentication and dashboards \|

| **Frontend** \| **CSS3** \| Modern, high-contrast stylesheet with
  responsive cards, form groups, and status badges \|

| **Frontend** \| **JavaScript (ES6+)** \| Dynamic DOM rendering,
  asynchronous fetch requests, Canvas image scaling, and auth guards \|

| **Backend** \| **Python** \| Core programming language for business
  logic and routing \|

| **Backend** \| **Flask** \| Lightweight WSGI microframework powering
  RESTful API endpoints \|

| **Security** \| **Werkzeug Security** \| Secure password hashing
  (`generate_password_hash`, `check_password_hash`) and session cookies
  \|

| **Database** \| **MySQL (TiDB Cloud)** \| Relational database engine
  for production with automatic SSL certificate verification \|

| **Database** \| **SQLite** \| Self-contained, zero-configuration
  fallback database engine for offline local execution \|

| **Email API** \| **Resend REST API** \| Transactional HTTPS email
  provider for password reset OTP delivery \|

| **Deployment** \| **Vercel** \| Serverless cloud hosting platform
  configured via `vercel.json` \|

------------------------------------------------------------------------

## 📁 Project Folder Structure

``` text

online-complaint-management-system/

│

├── api/

│   └── index.py               # Vercel serverless WSGI entry point

│

├── admin.html                 # Administrator Console (Grievance registry & triage)

├── app.py                     # Main Flask application & REST API endpoints

├── database.sql               # MySQL database schema

├── index.html                 # Authentication gateway (Login, Register, OTP Reset)

├── requirements.txt           # Python package dependencies

├── script.js                  # Frontend client logic, auth guards & API integration

├── student.html               # Student Portal (Complaint submission & tracking)

├── style.css                  # High-contrast, responsive UI styling

├── test_app.py                # Automated end-to-end unit test suite

├── vercel.json                # Vercel serverless routing configuration

└── README.md                  # Comprehensive project documentation
```

------------------------------------------------------------------------

## 🗄️ Database Design

The system implements a relational schema designed for data integrity,
user privacy, and fast query execution.

``` mermaid

erDiagram

    STUDENTS ||--o{ COMPLAINTS : submits

    STUDENTS ||--o{ PASSWORD_RESETS : requests

    STUDENTS {

        int id PK "AUTO_INCREMENT"

        varchar full_name "Student Full Name"

        varchar student_id UK "Unique Roll Number / College ID"

        varchar email UK "Unique College Email"

        varchar password "Werkzeug Hash"

        timestamp created_at "Registration Timestamp"

    }

    COMPLAINTS {

        int id PK "AUTO_INCREMENT"

        int complaint_no "Sequential Reference Number (#1, #2...)"

        varchar student_name "Student Name"

        varchar student_id "Student Roll Number"

        varchar category "Classroom, Lab, Hostel, Wi-Fi..."

        varchar title "Brief Subject"

        text description "Detailed Issue Narrative"

        longtext image_data "Optional Base64 Encoded Image"

        varchar status "Pending | In Progress | Resolved"

        timestamp created_at "Lodged Timestamp"

    }

    ADMINS {

        int id PK "AUTO_INCREMENT"

        varchar name "Admin Name"

        varchar email UK "Admin Email"

        varchar password "Werkzeug Hash"

        timestamp created_at "Created Timestamp"

    }

    PASSWORD_RESETS {

        varchar email PK "Student Email"

        varchar otp "6-Digit Secure OTP"

        int expires_at "Unix Expiration Timestamp"

    }
```

### Table Specifications

1.  **`students`**: Stores registered student profiles. Both `email` and
    `student_id` have unique constraints to prevent duplicate
    registrations.

2.  **`complaints`**: Stores submitted grievances.

    -   `complaint_no`: Indexed integer assigned sequentially
        (`MAX(complaint_no) + 1`), providing clean IDs independent of
        database auto-increment jumps.

    -   `image_data`: Stored as `LONGTEXT` (MySQL) or `TEXT` (SQLite)
        containing a Base64 data URL.

    -   Indexes on `(complaint_no)` and `(student_id)` ensure rapid
        student-scoped and admin-wide queries.

3.  **`admins`**: Stores privileged administrative accounts.

4.  **`password_resets`**: Stores active 6-digit OTP codes keyed by
    student email with a 10-minute expiration window.

------------------------------------------------------------------------

## ⚙️ Local Installation & Setup

### Prerequisites

-   **Python** installed on your system ([Download
    Python](https://www.python.org/downloads/))

-   **Git** installed on your system ([Download
    Git](https://git-scm.com/))

-   Optional: Local **MySQL / phpMyAdmin** (XAMPP / WampServer) or a
    free **TiDB Cloud** cluster. If MySQL is not present, the app will
    run on SQLite automatically.

### 1. Clone the Repository

``` bash

git clone https://github.com/ShaikhVaiz/online-complaint-management-system.git

cd online-complaint-management-system
```

### 2. Create and Activate a Virtual Environment

``` bash

# On Windows (Command Prompt / PowerShell)

python -m venv venv

venv\Scripts\activate

# On macOS / Linux

python3 -m venv venv

source venv/bin/activate
```

### 3. Install Dependencies

``` bash

pip install -r requirements.txt
```

------------------------------------------------------------------------

## 🔐 Environment Variables

The application requires a `SECRET_KEY` for Flask sessions. For local
development, configure it before starting the server. For production,
use a managed MySQL-compatible database (such as TiDB Cloud) and
configure its connection variables. SQLite is available as a local
fallback; on Vercel, `/tmp` storage is ephemeral and must not be treated
as persistent production storage.

| Variable \| Required? \| Default \| Description \|

\|---\|:---:\|:---:\|---\|

| `SECRET_KEY` \| Required \| None \| Secret used to sign Flask session
  cookies; set a strong private value in your environment \|
| `PORT` \| Optional \| `5000` \| Port for the local Flask development
  server \|

| `DATABASE_URL` \| Optional \| **None** \| Complete MySQL connection
  URI (e.g., `mysql://user:pass\@host:4000/db`) \|

| `MYSQL_HOST` / `TIDB_HOST` \| Optional \| `127.0.0.1` \| Remote MySQL
  / TiDB server hostname \|

| `MYSQL_PORT` / `TIDB_PORT` \| Optional \| `3306` \| MySQL server port
  \|

| `MYSQL_USER` / `TIDB_USER` \| Optional \| `root` \| Database username
  \|

| `MYSQL_PASSWORD` / `TIDB_PASSWORD` \| Optional \| **Empty** \|
  Database user password \|

| `MYSQL_DATABASE` / `TIDB_DATABASE` \| Optional \| `complaint_db` \|
  Database schema name \|

| `SQLITE_PATH` \| Optional \| `complaint_db.sqlite` \| Custom file path
  for SQLite database \|

| `RESEND_API_KEY` \| Optional \| **None** \| Resend API key for real
  email OTP delivery \|

| `SMTP_EMAIL` \| Optional \| **None** \| Sender email address for
  fallback SMTP \|

| `SMTP_PASSWORD` \| Optional \| **None** \| Google App Password / SMTP
  password \|

| `SMTP_HOST` \| Optional \| `smtp.gmail.com` \| SMTP relay server host
  \|

| `SMTP_PORT` \| Optional \| `587` \| SMTP relay port (TLS) \|

| `BREVO_API_KEY` \| Optional \| **None** \| Brevo API key for
  transactional email dispatch \|

> \[!NOTE\]

> If no MySQL connection is available, the application can fall back to
> SQLite. The local SQLite database file is intentionally excluded from
> Git because it may contain student and complaint records. A fresh
> local database may be initialized by the application; Vercel's `/tmp`
> filesystem is temporary.

------------------------------------------------------------------------

## ▶️ Running the Application

Before starting Flask, set a private session key.

``` powershell
$env:SECRET_KEY = "your-generated-secret-value"
```

Generate a strong value locally with:

``` powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Do not commit the generated value or share it publicly.

Start the local server:

``` bash

python app.py
```

Once started, the console will display:

``` text

\=================================================================

  COLLEGE ONLINE COMPLAINT MANAGEMENT SYSTEM

\=================================================================

[*] Server running on: http://127.0.0.1:5000

[*] Login Gateway    : http://127.0.0.1:5000/

[*] Student Portal   : http://127.0.0.1:5000/student.html

[*] Admin Portal     : http://127.0.0.1:5000/admin.html

-----------------------------------------------------------------
```

Open your browser and navigate to:

👉 **[http://127.0.0.1:5000](**http://127.0.0.1:5000**)**

------------------------------------------------------------------------

## 🧪 Running Automated Tests

The repository includes a comprehensive unit test suite in
[`test_app.py`](test_app.py) built on Python's native `unittest`
framework.

### Running the Test Suite

``` bash

python -m unittest discover -s . -p "test_*.py"
```

### Coverage

The test suite validates:

1.  `test_01_duplicate_email_registration` - Verifies duplicate email
    rejection with exact error message.

2.  `test_02_duplicate_roll_number_registration` - Verifies duplicate
    roll number rejection with exact error message.

3.  `test_03_successful_student_registration` - Tests registration flow
    with valid credentials.

4.  `test_04_student_login` - Validates student authentication and
    session persistence via `/api/me`.

5.  `test_05_admin_login` - Validates administrative authentication and
    role guards.

6.  `test_06_complaint_listing_and_details` - Confirms complaints list
    returns lightweight metadata with Base64 omitted.

7.  `test_07_complaint_image_viewing` - Tests image attachment and lazy
    loading via `/api/complaints/\<id>/image`.

8.  `test_08_complaint_status_updates` - Validates status transitions
    (`Pending` $\rightarrow$ `In Progress` $\rightarrow$ `Resolved`).

9.  `test_09_logout` - Confirms session destruction on logout.

10. `test_10_html_and_js_integrity` - Verifies presence and structure of
    critical DOM elements, CSS classes, and API endpoints.

------------------------------------------------------------------------

## 🚀 Deployment Guide

The application is architected for deployment on
[Vercel](https://vercel.com) using serverless Python functions.

### Architecture on Vercel

-   **WSGI Bridge**: [`api/index.py`](api/index.py) imports and exposes
    `app` from [`app.py`](app.py) as a serverless function handler.

-   **Routing**: [`vercel.json`](vercel.json) routes all incoming HTTP
    requests to `@vercel/python`.

-   **Database on Serverless**:

    -   Connects to a cloud database (such as **TiDB Cloud Serverless**
        or **AWS RDS MySQL**) using SSL certificates discovered
        automatically by `certifi`.

    -   In testing environments without a cloud database, falls back to
        `/tmp/complaint_db.sqlite`.

### Deploying Your Own Instance

1.  Fork or push this repository to your GitHub account.

2.  Import the project into your [Vercel
    Dashboard](https://vercel.com/new).

3.  Under **Project Settings $\rightarrow$ Environment Variables**,
    configure your database and email keys (e.g. `DATABASE_URL`,
    `RESEND_API_KEY`).

4.  Click **Deploy**. Vercel will build and provision your live
    serverless endpoint automatically.

------------------------------------------------------------------------

## 📸 Application Screenshots

### 1. Authentication Page
<p align="center">
  <img src="screenshots/01-login.png" width="85%" alt="Login Page">
</p>

### 2. Student Dashboard
<p align="center">
  <img src="screenshots/02-student-dashboard.png" width="85%" alt="Student Dashboard">
</p>

### 3. Submit Complaint
<p align="center">
  <img src="screenshots/03-submit-complaint.png" width="85%" alt="Submit Complaint">
</p>

### 4. Complaint Tracking
<p align="center">
  <img src="screenshots/04-complaint-tracking.png" width="85%" alt="Complaint Tracking">
</p>

### 5. Admin Dashboard
<p align="center">
  <img src="screenshots/05-admin-dashboard.png" width="85%" alt="Admin Dashboard">
</p>

### 6. Complaint Status Management
<p align="center">
  <img src="screenshots/06-status-management.png" width="85%" alt="Complaint Status Management">
</p>

------------------------------------------------------------------------

## 🔮 Future Improvements

-   [ ] **Email Status Notifications**: Automatically notify students
    via email when an administrator updates their grievance status to
    **In Progress** or **Resolved**.

-   [ ] **Department Assignment**: Route complaints directly to specific
    department heads (e.g. Facilities, Electrical, IT, Academic).

-   [ ] **Anonymous Submissions**: Optional anonymous grievance option
    for sensitive student feedback.

-   [ ] **Admin Audit Logs**: Historical audit log recording which
    administrator changed ticket status and when.

-   [ ] **Export to Excel / PDF**: Enable administrators to download
    monthly grievance reports in CSV or PDF format.

------------------------------------------------------------------------

## 👨‍💻 Author

-   **Developer:** [Shaikh Vaiz Faiyaz](https://github.com/ShaikhVaiz)

-   **Repository:**
    [online-complaint-management-system](https://github.com/ShaikhVaiz/online-complaint-management-system)
