CREATE DATABASE college_event;

USE college_event;

CREATE TABLE users(

id INT PRIMARY KEY AUTO_INCREMENT,

name VARCHAR(100),

email VARCHAR(100) UNIQUE,

password VARCHAR(255),

role VARCHAR(20)

);

CREATE TABLE events(

id INT PRIMARY KEY AUTO_INCREMENT,

title VARCHAR(100),

description TEXT,

event_date DATE,

event_time TIME,

venue VARCHAR(100),

category VARCHAR(50)

);

CREATE TABLE registrations(

id INT PRIMARY KEY AUTO_INCREMENT,

user_id INT,

event_id INT,

FOREIGN KEY(user_id) REFERENCES users(id),

FOREIGN KEY(event_id) REFERENCES events(id)

);