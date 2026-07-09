CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL
);