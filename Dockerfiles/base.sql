DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    gender VARCHAR(10),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    dob VARCHAR(64),
    registered VARCHAR(64),  
    phone VARCHAR(20),
    nationality VARCHAR(10),
    country VARCHAR(100),
    postcode VARCHAR(20)
);