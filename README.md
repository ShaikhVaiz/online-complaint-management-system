# Online Complaint Management System (Mini Project)

A lightweight, beginner-friendly college mini project built with **HTML5**, **CSS3**, **JavaScript**, and **MySQL** (with a lightweight Python API).

---

## 🎯 Key Features

- **Student Portal (`index.html`)**:
  - Lodge grievances online with Student Name, Roll No, Category, Title, and Description.
  - View all complaints and real-time status badges (Pending, In Progress, Resolved).
- **Admin Portal (`admin.html`)**:
  - Live summary statistics (Total, Pending, In Progress, Resolved).
  - Search and filter complaints by status.
  - 1-click status update dropdown (`Pending` ➔ `In Progress` ➔ `Resolved`).
  - Delete complaints if needed.
- **Database**:
  - Works with **MySQL** (`complaint_db`) via XAMPP.
  - Includes auto-fallback to SQLite so the project runs anywhere even without MySQL running.

---

## 💻 How to Run & Test Locally

### Step 1: Set Up MySQL Database (XAMPP)
1. Open **XAMPP Control Panel** and start **MySQL** and **Apache**.
2. Open your browser and go to: `http://localhost/phpmyadmin`
3. Click on the **SQL** tab and paste the contents of `database.sql`, or click **Import** and select `database.sql`.
4. Click **Go / Import**. The database `complaint_db` and table `complaints` will be created with sample data.

### Step 2: Run the Project
Open Command Prompt in this folder and run:
```bash
python app.py
```

Open your browser to:
- **Student Portal**: `http://127.0.0.1:5000/`
- **Admin Portal**: `http://127.0.0.1:5000/admin.html`

---

## 🚀 How to Deploy on Vercel via GitHub

### Step 1: Create a GitHub Repository
1. Go to [github.com](https://github.com) and click **New Repository**.
2. Name it `college-complaint-system` and click **Create repository**.
3. In your project folder, open terminal and run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - College Complaint System"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/college-complaint-system.git
   git push -u origin main
   ```

### Step 2: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
2. Click **Add New...** ➔ **Project**.
3. Select your `college-complaint-system` repository and click **Import**.
4. Leave all settings at default (`vercel.json` will automatically configure Python and routes).
5. Click **Deploy**.
6. Within 1 minute, your project is live with a free `https://your-project.vercel.app` domain!
