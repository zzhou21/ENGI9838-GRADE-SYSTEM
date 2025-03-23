-- Create database if not exists
CREATE DATABASE IF NOT EXISTS grade_system DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Switch to the database
USE grade_system;

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS assignments;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS users;

-- Create users table
-- Stores all users including students, teachers, and administrators
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)  UNIQUE NOT NULL,
    password    VARCHAR(255) NOT NULL,
    email       VARCHAR(100),
    role        ENUM('student','teacher','admin') DEFAULT 'student'
) ENGINE=InnoDB;

-- Create courses table
-- Contains information about courses offered
CREATE TABLE courses (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    course_code VARCHAR(50)  UNIQUE,
    description TEXT,
    teacher_id  INT NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create assignments table
-- Stores assignments created by teachers for specific courses
CREATE TABLE assignments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    course_id   INT NOT NULL,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    due_date    DATETIME,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create enrollments table
-- Stores many-to-many relationships between students and courses
CREATE TABLE enrollments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    course_id   INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (user_id, course_id)
) ENGINE=InnoDB;

-- Create submissions table
-- Stores student submissions for assignments
CREATE TABLE submissions (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id  INT NOT NULL,
    student_id     INT NOT NULL,
    file_path      VARCHAR(255),
    submitted_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_late        TINYINT(1) DEFAULT 0,
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Create grades table
-- Stores grades and feedback for submissions
CREATE TABLE grades (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    submission_id  INT NOT NULL,
    score          DECIMAL(5,2),
    feedback       TEXT,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_submission (submission_id)
) ENGINE=InnoDB;

