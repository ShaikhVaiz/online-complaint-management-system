#!/usr/bin/env python3
"""
Mini Project: Online Complaint Management System
Backend API & Web Server (Supports MySQL + SQLite Fallback)
Run locally: python app.py
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")
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

def get_db_connection():
    """Returns MySQL connection if available, otherwise falls back to SQLite."""
    global USE_SQLITE

    if not USE_SQLITE:
        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASS,
                database=MYSQL_DB,
                port=MYSQL_PORT,
                autocommit=True
            )
            return conn, "mysql"
        except Exception as e:
            # If database doesn't exist, try creating it
            try:
                import mysql.connector
                root_conn = mysql.connector.connect(
                    host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS, port=MYSQL_PORT, autocommit=True
                )
                cur = root_conn.cursor()
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}`")
                cur.execute(f"USE `{MYSQL_DB}`")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS complaints (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        student_name VARCHAR(100) NOT NULL,
                        student_id VARCHAR(50) NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        title VARCHAR(200) NOT NULL,
                        description TEXT NOT NULL,
                        status VARCHAR(50) DEFAULT 'Pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.close()
                root_conn.close()
                # Reconnect to newly created database
                conn = mysql.connector.connect(
                    host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS, database=MYSQL_DB, port=MYSQL_PORT, autocommit=True
                )
                return conn, "mysql"
            except Exception:
                USE_SQLITE = True

    # Fallback to local SQLite (zero-config, works everywhere including Vercel serverless)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            student_id TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn, "sqlite"

def init_seed_data():
    """Seeds sample complaints if database is empty."""
    conn, db_type = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM complaints")
        count = cur.fetchone()[0]
        if count == 0:
            sample_records = [
                ('Rahul Sharma', 'CS101', 'Hostel', 'Water Cooler Not Cooling', 'The water dispenser on 2nd floor is not cooling.', 'Pending'),
                ('Priya Patel', 'EC202', 'Laboratory', 'Lab System Mouse Not Working', 'Computer 14 in Electronics Lab has broken mouse.', 'In Progress'),
                ('Amit Kumar', 'ME305', 'Classroom', 'Fan Making Loud Noise', 'Ceiling fan near blackboard in Room 301 is vibrating.', 'Resolved')
            ]
            if db_type == "mysql":
                cur.executemany("""
                    INSERT INTO complaints (student_name, student_id, category, title, description, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, sample_records)
            else:
                cur.executemany("""
                    INSERT INTO complaints (student_name, student_id, category, title, description, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, sample_records)
                conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Notice: Initial seed skipped: {e}")

init_seed_data()

# -------------------------------------------------------------
# Static HTML Page Routes
# -------------------------------------------------------------
@app.route("/")
def serve_index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/admin")
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
# REST API Endpoints for Complaints
# -------------------------------------------------------------
@app.route("/api/complaints", methods=["GET"])
def get_complaints():
    """Retrieve all complaints sorted by newest first."""
    conn, db_type = get_db_connection()
    try:
        cur = conn.cursor(dictionary=True) if db_type == "mysql" else conn.cursor()
        cur.execute("SELECT * FROM complaints ORDER BY id DESC")
        rows = cur.fetchall()

        results = []
        for r in rows:
            if db_type == "sqlite":
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
            else:
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
    """Lodge a new student complaint."""
    data = request.get_json() or request.form
    name = (data.get("student_name") or "").strip()
    sid = (data.get("student_id") or "").strip()
    cat = (data.get("category") or "").strip()
    title = (data.get("title") or "").strip()
    desc = (data.get("description") or "").strip()

    if not name or not sid or not cat or not title or not desc:
        return jsonify({"success": False, "message": "All fields are required"}), 400

    conn, db_type = get_db_connection()
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
    """Admin updates the status of a complaint."""
    data = request.get_json() or request.form
    new_status = data.get("status")

    if new_status not in ["Pending", "In Progress", "Resolved"]:
        return jsonify({"success": False, "message": "Invalid status value"}), 400

    conn, db_type = get_db_connection()
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
    """Admin deletes a complaint."""
    conn, db_type = get_db_connection()
    try:
        cur = conn.cursor()
        if db_type == "mysql":
            cur.execute("DELETE FROM complaints WHERE id = %s", (complaint_id,))
        else:
            cur.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
            conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": f"Complaint #{complaint_id} deleted"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# -------------------------------------------------------------
# Local Development Runner
# -------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 65)
    print("  COLLEGE ONLINE COMPLAINT MANAGEMENT SYSTEM (Mini Project)")
    print("=" * 65)
    print(f"[*] Server running on: http://127.0.0.1:{port}")
    print(f"[*] Student Portal   : http://127.0.0.1:{port}/")
    print(f"[*] Admin Portal     : http://127.0.0.1:{port}/admin.html")
    print("-" * 65)
    app.run(host="0.0.0.0", port=port, debug=True)
