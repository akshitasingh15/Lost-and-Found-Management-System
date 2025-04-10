-- schema.sql

CREATE DATABASE IF NOT EXISTS lost_found_db;
USE lost_found_db;

CREATE TABLE IF NOT EXISTS Lost_Items (
    lost_id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(100),
    description TEXT,
    lost_location VARCHAR(255),
    lost_date DATE,
    status ENUM('Pending', 'Found', 'Closed') DEFAULT 'Pending'
);

CREATE TABLE IF NOT EXISTS Found_Items (
    found_id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(100),
    description TEXT,
    found_location VARCHAR(255),
    found_date DATE,
    status ENUM('Pending', 'Claimed', 'Closed') DEFAULT 'Pending'
)
