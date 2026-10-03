-- ========================================================
-- Mini Project: Online Complaint Management System
-- Database Schema for MySQL
-- ========================================================

CREATE DATABASE IF NOT EXISTS complaint_db;
USE complaint_db;

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

-- Sample Data for Initial Testing
INSERT INTO complaints (student_name, student_id, category, title, description, status) 
VALUES
('Rahul Sharma', 'CS101', 'Hostel', 'Water Cooler Not Cooling', 'The water dispenser on 2nd floor is not cooling water.', 'Pending'),
('Priya Patel', 'EC202', 'Laboratory', 'Lab System Mouse Not Working', 'Computer 14 in Electronics Lab has broken scroll wheel.', 'In Progress'),
('Amit Kumar', 'ME305', 'Classroom', 'Fan Making Loud Noise', 'Ceiling fan near blackboard in Room 301 is vibrating.', 'Resolved');
