#!/usr/bin/env python3
"""
Mini Project: Online Complaint Management System
Backend API with Student & Admin Authentication (MySQL + SQLite Fallback)
Run command: python app.py
"""

import os
import sys
import json
import random
import time
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import Flask, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = "eduresolve_mini_project_secret_key_2026"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------------------
# Real Email Dispatcher (Gmail SMTP)
# -------------------------------------------------------------
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "").strip()
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "").strip()
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com").strip()
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))

def send_real_email_otp(to_email, otp_code):
    """Sends real OTP email via Gmail SMTP if credentials are configured in Vercel/env."""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return False, "SMTP not configured"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🔐 Password Reset OTP - Online Complaint Management System"
        msg["From"] = f"Online Complaint Portal <{SMTP_EMAIL}>"
        msg["To"] = to_email

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background: #f8fafc; padding: 20px; color: #0f172a;">
            <div style="max-width: 500px; margin: auto; background: #ffffff; border-radius: 12px; padding: 28px; border: 1px solid #e2e8f0;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h2 style="color: #1e3a8a; margin: 0;">Online Complaint Management System</h2>
                    <p style="color: #64748b; font-size: 14px; margin-top: 5px;">Campus Grievance Portal</p>
                </div>
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                <p>Hello,</p>
                <p>You requested a password reset for your student account (<strong>{to_email}</strong>).</p>
                <p>Your 6-digit One-Time Password (OTP) is:</p>
                <div style="background: #eff6ff; border: 1.5px dashed #3b82f6; border-radius: 10px; padding: 18px; text-align: center; margin: 25px 0;">
                    <span style="font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #1d4ed8;">{otp_code}</span>
                </div>
                <p style="color: #64748b; font-size: 13px;">
                    ⏱️ This OTP is valid for <strong>10 minutes</strong>. Do not share it with anyone.
                </p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully"
    except Exception as e:
        print(f"SMTP error sending OTP: {e}")
        return False, str(e)

# -------------------------------------------------------------
# Database Connection Manager (Cloud MySQL with SQLite fallback)
# -------------------------------------------------------------
from urllib.parse import urlparse

DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("MYSQL_URL") or os.environ.get("TIDB_URL")
if DATABASE_URL and ("mysql" in DATABASE_URL or "tidb" in DATABASE_URL):
    parsed = urlparse(DATABASE_URL)
    MYSQL_HOST = parsed.hostname or "127.0.0.1"
    MYSQL_USER = parsed.username or "root"
    MYSQL_PASS = parsed.password or ""
    MYSQL_DB   = (parsed.path or "").lstrip("/") or "complaint_db"
    MYSQL_PORT = parsed.port or 3306
else:
    MYSQL_HOST = os.environ.get("MYSQL_HOST") or os.environ.get("TIDB_HOST") or "127.0.0.1"
    MYSQL_USER = os.environ.get("MYSQL_USER") or os.environ.get("TIDB_USER") or "root"
    MYSQL_PASS = os.environ.get("MYSQL_PASSWORD") or os.environ.get("TIDB_PASSWORD") or ""
    MYSQL_DB   = os.environ.get("MYSQL_DATABASE") or os.environ.get("TIDB_DATABASE") or "complaint_db"
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT") or os.environ.get("TIDB_PORT") or 3306)

import shutil

USE_SQLITE = False
if os.environ.get("VERCEL"):
    SQLITE_PATH = "/tmp/complaint_db.sqlite"
    src_db = os.path.join(BASE_DIR, "complaint_db.sqlite")
    if not os.path.exists(SQLITE_PATH) and os.path.exists(src_db):
        try:
            shutil.copyfile(src_db, SQLITE_PATH)
        except Exception:
            pass
else:
    SQLITE_PATH = os.path.join(BASE_DIR, "complaint_db.sqlite")

LAST_DB_ERROR = None

def connect_mysql():
    """Attempts connection to MySQL with SSL auto-negotiation for Cloud providers (TiDB, Aiven, etc.)."""
    global LAST_DB_ERROR
    import mysql.connector

    ca_file = None
    try:
        import certifi
        ca_file = certifi.where()
    except Exception:
        for candidate in [
            "/etc/ssl/certs/ca-certificates.crt",
            "/etc/pki/tls/certs/ca-bundle.crt",
            "/etc/ssl/cert.pem"
        ]:
            if os.path.exists(candidate):
                ca_file = candidate
                break

    base_params = {
        "host": MYSQL_HOST,
        "user": MYSQL_USER,
        "password": MYSQL_PASS,
        "database": MYSQL_DB,
        "port": MYSQL_PORT,
        "autocommit": True
    }

    # If remote host (TiDB Cloud, Aiven, etc.), use SSL with CA cert
    if MYSQL_HOST not in ("127.0.0.1", "localhost"):
        try:
            ssl_params = dict(base_params)
            if ca_file:
                ssl_params["ssl_ca"] = ca_file
                ssl_params["ssl_verify_cert"] = True
            else:
                ssl_params["ssl_disabled"] = False
            return mysql.connector.connect(**ssl_params)
        except Exception as e1:
            try:
                ssl_params2 = dict(base_params)
                ssl_params2["ssl_disabled"] = False
                return mysql.connector.connect(**ssl_params2)
            except Exception:
                pass
            try:
                return mysql.connector.connect(**base_params)
            except Exception:
                LAST_DB_ERROR = str(e1)
                raise e1

    # Local direct connection
    return mysql.connector.connect(**base_params)

def get_db():
    """Returns (connection, db_type)."""
    global USE_SQLITE, LAST_DB_ERROR

    if not USE_SQLITE:
        try:
            conn = connect_mysql()
            LAST_DB_ERROR = None
            return conn, "mysql"
        except Exception as err:
            LAST_DB_ERROR = str(err)
            # Try to auto-create MySQL database if permitted
            try:
                import mysql.connector
                root_conn = mysql.connector.connect(
                    host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS, port=MYSQL_PORT, autocommit=True
                )
                cur = root_conn.cursor()
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}`")
                cur.close()
                root_conn.close()

                conn = connect_mysql()
                LAST_DB_ERROR = None
                return conn, "mysql"
            except Exception as e2:
                LAST_DB_ERROR = f"Connection failed: {err} | DB Create: {e2}"
                if os.environ.get("MYSQL_HOST") or os.environ.get("DATABASE_URL") or os.environ.get("TIDB_HOST"):
                    print(f"Notice: Remote MySQL connection failed ({LAST_DB_ERROR}). Falling back to SQLite.")
                USE_SQLITE = True

    # Fallback: SQLite
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    create_tables(conn.cursor(), "sqlite")
    conn.commit()
    return conn, "sqlite"

def create_tables(cursor, db_type):
    """Creates schema for admins, students, complaints, and password_resets."""
    if db_type == "mysql":
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                student_id VARCHAR(50) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(100) NOT NULL,
                student_id VARCHAR(50) NOT NULL,
                category VARCHAR(50) NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) AUTO_ID_CACHE = 1;
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                email VARCHAR(100) PRIMARY KEY,
                otp VARCHAR(10) NOT NULL,
                expires_at INT NOT NULL
            );
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                student_id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                student_id TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                email TEXT PRIMARY KEY,
                otp TEXT NOT NULL,
                expires_at INTEGER NOT NULL
            );
        """)

def seed_defaults():
    """Seeds default admin and test student account if not present."""
    conn, db_type = get_db()
    try:
        cur = conn.cursor()
        create_tables(cur, db_type)

        # Normalize TiDB 30000+ IDs and enforce sequential IDs starting from 1
        if db_type == "mysql":
            try:
                cur.execute("ALTER TABLE complaints AUTO_ID_CACHE = 1")
            except Exception:
                pass
            try:
                cur.execute("UPDATE complaints SET id = (id - 30000) WHERE id >= 30001")
            except Exception:
                pass
        
        # Check admin
        cur.execute("SELECT id FROM admins WHERE email = 'admin@college.com'")
        if not cur.fetchone():
            admin_pwd = generate_password_hash("Admin@123")
            if db_type == "mysql":
                cur.execute("INSERT INTO admins (name, email, password) VALUES (%s, %s, %s)",
                            ("Administrator", "admin@college.com", admin_pwd))
            else:
                cur.execute("INSERT INTO admins (name, email, password) VALUES (?, ?, ?)",
                            ("Administrator", "admin@college.com", admin_pwd))

        # Check sample student
        cur.execute("SELECT id FROM students WHERE email = 'rahul.sharma@college.com'")
        if not cur.fetchone():
            stu_pwd = generate_password_hash("Student@123")
            if db_type == "mysql":
                cur.execute("INSERT INTO students (full_name, student_id, email, password) VALUES (%s, %s, %s, %s)",
                            ("Rahul Sharma", "CS101", "rahul.sharma@college.com", stu_pwd))
            else:
                cur.execute("INSERT INTO students (full_name, student_id, email, password) VALUES (?, ?, ?, ?)",
                            ("Rahul Sharma", "CS101", "rahul.sharma@college.com", stu_pwd))

        # Check sample complaints
        cur.execute("SELECT COUNT(*) FROM complaints")
        cnt = cur.fetchone()[0]
        if cnt == 0:
            samples = [
                ('Rahul Sharma', 'CS101', 'Hostel', 'Water Cooler Not Cooling', 'Water dispenser on 2nd floor is not cooling.', 'Pending'),
                ('Rahul Sharma', 'CS101', 'Laboratory', 'Lab System Mouse Broken', 'Computer 14 in Electronics Lab has broken mouse.', 'In Progress'),
                ('Rahul Sharma', 'CS101', 'Classroom', 'Fan Making Noise', 'Ceiling fan near blackboard in Room 301 is vibrating.', 'Resolved')
            ]
            if db_type == "mysql":
                cur.executemany("INSERT INTO complaints (student_name, student_id, category, title, description, status) VALUES (%s, %s, %s, %s, %s, %s)", samples)
            else:
                cur.executemany("INSERT INTO complaints (student_name, student_id, category, title, description, status) VALUES (?, ?, ?, ?, ?, ?)", samples)
        
        if db_type == "sqlite":
            conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Notice: Seed verification: {e}")

seed_defaults()

# -------------------------------------------------------------
# Static HTML Page Routes
# -------------------------------------------------------------
@app.route("/")
@app.route("/index.html")
@app.route("/login.html")
def serve_index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/student.html")
def serve_student():
    return send_from_directory(BASE_DIR, "student.html")

@app.route("/admin.html")
def serve_admin():
    return send_from_directory(BASE_DIR, "admin.html")

@app.route("/style.css")
def serve_css():
    return send_from_directory(BASE_DIR, "style.css")

@app.route("/script.js")
def serve_js():
    return send_from_directory(BASE_DIR, "script.js")

# -------------------------------------------------------------
# Authentication API
# -------------------------------------------------------------
@app.route("/api/register", methods=["POST"])
def register():
    """Register a new student account."""
    data = request.get_json() or request.form
    name = (data.get("full_name") or "").strip()
    sid = (data.get("student_id") or "").strip()
    email = (data.get("email") or "").strip().lower()
    pwd = data.get("password") or ""

    if not name or not sid or not email or not pwd:
        return jsonify({"success": False, "message": "All fields are required."}), 400
    if len(pwd) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400

    conn, db_type = get_db()
    try:
        cur = conn.cursor()
        if db_type == "mysql":
            cur.execute("SELECT id FROM students WHERE email = %s OR student_id = %s", (email, sid))
        else:
            cur.execute("SELECT id FROM students WHERE email = ? OR student_id = ?", (email, sid))
        
        if cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": "A student with this Email or Roll Number is already registered."}), 400

        hashed_pwd = generate_password_hash(pwd)
        if db_type == "mysql":
            cur.execute("INSERT INTO students (full_name, student_id, email, password) VALUES (%s, %s, %s, %s)",
                        (name, sid, email, hashed_pwd))
        else:
            cur.execute("INSERT INTO students (full_name, student_id, email, password) VALUES (?, ?, ?, ?)",
                        (name, sid, email, hashed_pwd))
            conn.commit()

        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Student registered successfully! Please log in."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/login", methods=["POST"])
def login():
    """Authenticate student or administrator."""
    data = request.get_json() or request.form
    role = data.get("role", "student")
    ident = (data.get("identifier") or "").strip()
    pwd = data.get("password") or ""

    if not ident or not pwd:
        return jsonify({"success": False, "message": "Please enter both credentials."}), 400

    conn, db_type = get_db()
    try:
        cur = conn.cursor(dictionary=True) if db_type == "mysql" else conn.cursor()

        if role == "admin":
            if db_type == "mysql":
                cur.execute("SELECT * FROM admins WHERE email = %s", (ident.lower(),))
            else:
                cur.execute("SELECT * FROM admins WHERE email = ?", (ident.lower(),))
            admin = cur.fetchone()

            if admin and check_password_hash(admin["password"], pwd):
                session["role"] = "admin"
                session["user_id"] = admin["id"]
                session["user_name"] = admin["name"]
                session["email"] = admin["email"]
                cur.close()
                conn.close()
                return jsonify({"success": True, "role": "admin"})
            else:
                cur.close()
                conn.close()
                return jsonify({"success": False, "message": "Invalid administrator email or password."}), 401
        else:
            # Student Login (via Email or Roll No)
            if db_type == "mysql":
                cur.execute("SELECT * FROM students WHERE email = %s OR student_id = %s", (ident.lower(), ident))
            else:
                cur.execute("SELECT * FROM students WHERE email = ? OR student_id = ?", (ident.lower(), ident))
            student = cur.fetchone()

            if student and check_password_hash(student["password"], pwd):
                session["role"] = "student"
                session["user_id"] = student["id"]
                session["user_name"] = student["full_name"]
                session["student_id"] = student["student_id"]
                session["email"] = student["email"]
                cur.close()
                conn.close()
                return jsonify({"success": True, "role": "student"})
            else:
                cur.close()
                conn.close()
                return jsonify({"success": False, "message": "Invalid student email/roll number or password."}), 401

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -------------------------------------------------------------
# Forgot Password via Email OTP Endpoints
# -------------------------------------------------------------
otp_store = {}

@app.route("/api/forgot-password/send-otp", methods=["POST"])
def send_otp():
    """Generates and sends a 6-digit OTP to the registered student email."""
    data = request.get_json() or request.form
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"success": False, "message": "Please enter your registered college email."}), 400

    conn, db_type = get_db()
    try:
        cur = conn.cursor(dictionary=True) if db_type == "mysql" else conn.cursor()
        if db_type == "mysql":
            cur.execute("SELECT id, full_name, email FROM students WHERE email = %s", (email,))
        else:
            cur.execute("SELECT id, full_name, email FROM students WHERE email = ?", (email,))
        
        student = cur.fetchone()
        if not student:
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": "No student account found with this email address."}), 404

        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        expires_at = int(time.time() + 600)  # valid for 10 minutes

        # 1. Save in Flask session cookie (persists across serverless instances in client browser)
        session["reset_email"] = email
        session["reset_otp"] = otp_code
        session["reset_expires"] = expires_at

        # 2. Save in database password_resets table
        try:
            if db_type == "mysql":
                cur.execute("""
                    INSERT INTO password_resets (email, otp, expires_at)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE otp = VALUES(otp), expires_at = VALUES(expires_at)
                """, (email, otp_code, expires_at))
            else:
                cur.execute("""
                    INSERT OR REPLACE INTO password_resets (email, otp, expires_at)
                    VALUES (?, ?, ?)
                """, (email, otp_code, expires_at))
                conn.commit()
            cur.close()
            conn.close()
        except Exception as dbe:
            print(f"Notice: Password reset DB record: {dbe}")
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

        # 3. Save in in-memory dict as backup
        otp_store[email] = {
            "otp": otp_code,
            "expires_at": expires_at
        }

        print(f"\n[EMAIL OTP DISPATCH] ===============================")
        print(f"To: {email}")
        print(f"Subject: Your Password Reset OTP for Online Complaint Portal")
        print(f"OTP Code: {otp_code} (Valid for 10 minutes)")
        print(f"======================================================\n")

        # 4. Dispatch real email via Gmail SMTP
        sent_real, smtp_msg = send_real_email_otp(email, otp_code)

        if sent_real:
            return jsonify({
                "success": True,
                "real_email_sent": True,
                "message": f"6-digit OTP has been sent directly to your Gmail inbox ({email}). Please check your inbox or spam folder."
            })
        else:
            print(f"Notice: Real SMTP dispatch not active: {smtp_msg}")
            return jsonify({
                "success": True,
                "real_email_sent": False,
                "demo_otp": otp_code,
                "message": f"OTP generated! (Gmail SMTP not configured: use code below for demo)."
            })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/forgot-password/verify-reset", methods=["POST"])
def verify_and_reset():
    """Verifies OTP and updates the student password in database."""
    data = request.get_json() or request.form
    email = (data.get("email") or "").strip().lower()
    otp_entered = (data.get("otp") or "").strip()
    new_password = data.get("new_password") or ""

    if not email or not otp_entered or not new_password:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "New password must be at least 6 characters long."}), 400

    now = time.time()
    valid = False

    # 1. Check Flask signed session cookie
    if session.get("reset_email") == email and session.get("reset_otp") == otp_entered:
        if now <= session.get("reset_expires", 0):
            valid = True

    # 2. Check Database password_resets table
    if not valid:
        try:
            conn, db_type = get_db()
            cur = conn.cursor(dictionary=True) if db_type == "mysql" else conn.cursor()
            if db_type == "mysql":
                cur.execute("SELECT otp, expires_at FROM password_resets WHERE email = %s", (email,))
            else:
                cur.execute("SELECT otp, expires_at FROM password_resets WHERE email = ?", (email,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                r_otp = row["otp"] if isinstance(row, dict) else row[0]
                r_exp = row["expires_at"] if isinstance(row, dict) else row[1]
                if str(r_otp) == otp_entered and now <= int(r_exp):
                    valid = True
        except Exception as e_db:
            print(f"Notice: OTP DB check: {e_db}")

    # 3. Check in-memory store
    if not valid and email in otp_store:
        record = otp_store[email]
        if record["otp"] == otp_entered and now <= record["expires_at"]:
            valid = True

    if not valid:
        return jsonify({"success": False, "message": "Invalid or expired OTP code. Please check and re-enter."}), 400

    # OTP is valid, update student password in database
    conn, db_type = get_db()
    try:
        cur = conn.cursor()
        hashed_pwd = generate_password_hash(new_password)

        if db_type == "mysql":
            cur.execute("UPDATE students SET password = %s WHERE email = %s", (hashed_pwd, email))
            cur.execute("DELETE FROM password_resets WHERE email = %s", (email,))
        else:
            cur.execute("UPDATE students SET password = ? WHERE email = ?", (hashed_pwd, email))
            cur.execute("DELETE FROM password_resets WHERE email = ?", (email,))
            conn.commit()

        cur.close()
        conn.close()

        # Invalidate OTP stores
        session.pop("reset_otp", None)
        session.pop("reset_email", None)
        session.pop("reset_expires", None)
        otp_store.pop(email, None)

        return jsonify({
            "success": True,
            "message": "Password reset successfully! You can now log in with your new password."
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/db-status", methods=["GET"])
def db_status():
    """Diagnostic endpoint to inspect active database engine and health."""
    global USE_SQLITE, LAST_DB_ERROR
    conn, db_type = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM students")
        row = cur.fetchone()
        stu_cnt = row[0] if row else 0
        cur.execute("SELECT COUNT(*) FROM complaints")
        row2 = cur.fetchone()
        comp_cnt = row2[0] if row2 else 0
        cur.close()
        conn.close()
        return jsonify({
            "status": "connected",
            "active_database": db_type,
            "host": MYSQL_HOST if db_type == "mysql" else "local_sqlite",
            "database_name": MYSQL_DB if db_type == "mysql" else "complaint_db.sqlite",
            "total_students": stu_cnt,
            "total_complaints": comp_cnt,
            "is_vercel": bool(os.environ.get("VERCEL")),
            "mysql_last_error": LAST_DB_ERROR
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "active_database": db_type,
            "error": str(e),
            "mysql_last_error": LAST_DB_ERROR
        }), 500

@app.route("/api/me", methods=["GET"])
def get_current_user():
    """Returns session user details for client-side authentication guards."""
    if "role" in session:
        return jsonify({
            "logged_in": True,
            "role": session.get("role"),
            "name": session.get("user_name"),
            "student_id": session.get("student_id"),
            "email": session.get("email")
        })
    return jsonify({"logged_in": False})

@app.route("/api/logout", methods=["POST"])
def logout():
    """Clears user session."""
    session.clear()
    return jsonify({"success": True, "message": "Signed out successfully."})

# -------------------------------------------------------------
# Complaints API
# -------------------------------------------------------------
@app.route("/api/complaints", methods=["GET"])
def get_complaints():
    """Fetch complaints list (filtered by student if logged in as student)."""
    conn, db_type = get_db()
    try:
        cur = conn.cursor(dictionary=True) if db_type == "mysql" else conn.cursor()
        
        # If student is logged in, show only their complaints
        if session.get("role") == "student" and session.get("student_id"):
            sid = session["student_id"]
            if db_type == "mysql":
                cur.execute("SELECT * FROM complaints WHERE student_id = %s ORDER BY id DESC", (sid,))
            else:
                cur.execute("SELECT * FROM complaints WHERE student_id = ? ORDER BY id DESC", (sid,))
        else:
            # Admin sees all complaints
            cur.execute("SELECT * FROM complaints ORDER BY id DESC")
        
        rows = cur.fetchall()
        results = []
        for r in rows:
            raw_id = r["id"]
            # TiDB Serverless allocates auto_increment in batches starting from 30001; normalize so IDs start from 1
            normalized_id = (raw_id - 30000) if raw_id >= 30001 else raw_id
            results.append({
                "id": normalized_id,
                "student_name": r["student_name"],
                "student_id": r["student_id"],
                "category": r["category"],
                "title": r["title"],
                "description": r["description"],
                "status": r["status"],
                "created_at": str(r["created_at"])
            })
        cur.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e), "message": "Failed to fetch complaints"}), 500

@app.route("/api/complaints", methods=["POST"])
def create_complaint():
    """Student lodges a new grievance."""
    data = request.get_json() or request.form
    name = (data.get("student_name") or session.get("user_name") or "").strip()
    sid = (data.get("student_id") or session.get("student_id") or "").strip()
    cat = (data.get("category") or "").strip()
    title = (data.get("title") or "").strip()
    desc = (data.get("description") or "").strip()

    if not name or not sid or not cat or not title or not desc:
        return jsonify({"success": False, "message": "All fields are required."}), 400

    conn, db_type = get_db()
    try:
        cur = conn.cursor()
        if db_type == "mysql":
            cur.execute("""
                INSERT INTO complaints (student_name, student_id, category, title, description, status)
                VALUES (%s, %s, %s, %s, %s, 'Pending')
            """, (name, sid, cat, title, desc))
            raw_id = cur.lastrowid
        else:
            cur.execute("""
                INSERT INTO complaints (student_name, student_id, category, title, description, status)
                VALUES (?, ?, ?, ?, ?, 'Pending')
            """, (name, sid, cat, title, desc))
            conn.commit()
            raw_id = cur.lastrowid
        cur.close()
        conn.close()
        new_id = (raw_id - 30000) if raw_id >= 30001 else raw_id
        return jsonify({"success": True, "id": new_id, "message": "Complaint submitted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/complaints/<int:complaint_id>/status", methods=["PUT", "POST"])
def update_complaint_status(complaint_id):
    """Admin updates grievance status."""
    data = request.get_json() or request.form
    new_status = data.get("status")

    if new_status not in ["Pending", "In Progress", "Resolved"]:
        return jsonify({"success": False, "message": "Invalid status value"}), 400

    conn, db_type = get_db()
    try:
        cur = conn.cursor()
        alt_id = complaint_id + 30000 if complaint_id < 30000 else complaint_id - 30000
        if db_type == "mysql":
            cur.execute("UPDATE complaints SET status = %s WHERE id = %s OR id = %s", (new_status, complaint_id, alt_id))
        else:
            cur.execute("UPDATE complaints SET status = ? WHERE id = ? OR id = ?", (new_status, complaint_id, alt_id))
            conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": f"Status updated to {new_status}"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/complaints/<int:complaint_id>", methods=["DELETE"])
def delete_complaint(complaint_id):
    """Admin deletes a grievance record."""
    conn, db_type = get_db()
    try:
        cur = conn.cursor()
        alt_id = complaint_id + 30000 if complaint_id < 30000 else complaint_id - 30000
        if db_type == "mysql":
            cur.execute("DELETE FROM complaints WHERE id = %s OR id = %s", (complaint_id, alt_id))
        else:
            cur.execute("DELETE FROM complaints WHERE id = ? OR id = ?", (complaint_id, alt_id))
            conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": f"Complaint #{complaint_id} deleted."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -------------------------------------------------------------
# Local Development Server Runner
# -------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 65)
    print("  COLLEGE ONLINE COMPLAINT MANAGEMENT SYSTEM")
    print("=" * 65)
    print(f"[*] Server running on: http://127.0.0.1:{port}")
    print(f"[*] Login Gateway    : http://127.0.0.1:{port}/")
    print(f"[*] Student Portal   : http://127.0.0.1:{port}/student.html")
    print(f"[*] Admin Portal     : http://127.0.0.1:{port}/admin.html")
    print("-" * 65)
    print("Default Credentials:")
    print("  Student: rahul.sharma@college.com | Password: Student@123")
    print("  Admin:   admin@college.com        | Password: Admin@123")
    print("-" * 65)
    app.run(host="0.0.0.0", port=port, debug=True)
