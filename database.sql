-- ========================================================
-- Mini Project: Online Complaint Management System
-- Database Schema for MySQL
-- ========================================================

CREATE DATABASE IF NOT EXISTS complaint_db;
USE complaint_db;

-- 1. Admins Table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Students Table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    student_id VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Complaints Table
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

-- Default Admin Account (Email: admin@college.com | Password: Admin@123)
-- (Password hash generated using Werkzeug / scrypt / pbkdf2)
INSERT INTO admins (name, email, password) 
VALUES ('System Administrator', 'admin@college.com', 'scrypt:32768:8:1$7tQz7B12b3r$f791e847ceba06a383b4b5e28a556391d8be698f2441c2a11b6953284ff0d6480f2d7a22ef7a6411f185ef3763f9232c9fc2d37c862a9332be2495bb3dbeae84')
ON DUPLICATE KEY UPDATE email=email;

-- Sample Student Account (Email: rahul.sharma@college.com | Roll: CS101 | Password: Student@123)
INSERT INTO students (full_name, student_id, email, password)
VALUES ('Rahul Sharma', 'CS101', 'rahul.sharma@college.com', 'scrypt:32768:8:1$8mKl5F82a9c$b214f5298a0d927a0890bf7061d4e73dbd632f056d6163351d3b0c6df6ba5e4905b38d3ab14d7970d49b25b6a71cb0a8801d017b2b73ec8b0f805b8e9069d80c')
ON DUPLICATE KEY UPDATE email=email;

-- Initial Sample Complaints
INSERT INTO complaints (student_name, student_id, category, title, description, status) 
VALUES
('Rahul Sharma', 'CS101', 'Hostel', 'Water Cooler Not Cooling', 'Water dispenser on 2nd floor is not cooling.', 'Pending'),
('Rahul Sharma', 'CS101', 'Laboratory', 'Lab System Mouse Broken', 'Computer 14 in Electronics Lab has broken mouse.', 'In Progress'),
('Rahul Sharma', 'CS101', 'Classroom', 'Fan Making Noise', 'Ceiling fan near blackboard in Room 301 is vibrating.', 'Resolved');
