CREATE DATABASE evoting;

USE evoting;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(15) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    voter_id VARCHAR(50) UNIQUE,
    has_voted BOOLEAN DEFAULT FALSE
);

CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE, 
    party VARCHAR(255) NOT NULL,                     
    bio TEXT
);


CREATE TABLE votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    voter_id VARCHAR(20) NOT NULL,
    candidate_id INT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

CREATE TABLE voters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(15) UNIQUE NOT NULL,
    voter_id VARCHAR(20) UNIQUE NOT NULL
);


-- INSERT INTO candidates (name, party, bio) 
-- VALUES 
--     ('MOHUN BAGAN AC', 'The Mariners', 'Indian Professional Multi-Sports Club'),
--     ('EAST BENGAL FC', 'The Emamis', 'Indian Professional Football Club');


SHOW TABLES;
select * from voters;
describe votes
