#!/usr/bin/env python3
"""
Mini Project: Online Complaint Management System
Backend API with Student & Admin Authentication (MySQL + SQLite Fallback)
Run command: python app.py
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder=".", static_url_path="")
app.secret_key = "eduresolve_mini_project_secret_key_2026"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------------------
# Database Connection Manager (MySQL with SQLite fallback)
# -------------------------------------------------------------
MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASS = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DB   = os.environ.get("MYSQL_DATABASE", "complaint_db")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))

USE_SQLITE = False
SQLITE_PATH = os.path.join(BASE_DIR, "complaint_db.sqlite")

def get_db():
    """Returns (connection, db_type)."""
    global USE_SQLITE

    if not USE_SQLITE:
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS,
                database=MYSQL_DB, port=MYSQL_PORT, autocommit=True
            )
            return conn, "mysql"
        except Exception:
            # Try to auto-create MySQL database and tables
            try:
                import mysql.connector
                root_conn = mysql.connector.connect(
                    host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS, port=MYSQL_PORT, autocommit=True
                )
                cur = root_conn.cursor()
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}`")
                cur.execute(f"USE `{MYSQL_DB}`")
                create_tables(cur, "mysql")
                cur.close()
                root_conn.close()

                conn = mysql.connector.connect(
                    host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS,
                    database=MYSQL_DB, port=MYSQL_PORT, autocommit=True
                )
                return conn, "mysql"
            except Exception:
                USE_SQLITE = True

    # Fallback: SQLite
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    create_tables(conn.cursor(), "sqlite")
    conn.commit()
    return conn, "sqlite"

def create_tables(cursor, db_type):
    """Creates schema for admins, students, and complaints."""
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

def seed_defaults():
    """Seeds default admin and test student account if not present."""
    conn, db_type = get_db()
    try:
        cur = conn.cursor()
        
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
            results.append({
                "id": r["id"],
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
            new_id = cur.lastrowid
        else:
            cur.execute("""
                INSERT INTO complaints (student_name, student_id, category, title, description, status)
                VALUES (?, ?, ?, ?, ?, 'Pending')
            """, (name, sid, cat, title, desc))
            conn.commit()
            new_id = cur.lastrowid
        cur.close()
        conn.close()
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
        if db_type == "mysql":
            cur.execute("UPDATE complaints SET status = %s WHERE id = %s", (new_status, complaint_id))
        else:
            cur.execute("UPDATE complaints SET status = ? WHERE id = ?", (new_status, complaint_id))
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
        if db_type == "mysql":
            cur.execute("DELETE FROM complaints WHERE id = %s", (complaint_id,))
        else:
            cur.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
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
