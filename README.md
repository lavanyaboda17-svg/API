# BlogApp

A simple Flask-based blogging application with user registration, login, and post creation features. Built with Flask, Flask-SQLAlchemy, and PostgreSQL.

## Features

- User registration with password hashing (Werkzeug security)
- User login with session-based authentication
- Session timeout (auto-logout after inactivity)
- Create and view blog posts
- User profile pages
- Logout functionality

## Tech Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL
- **ORM:** Flask-SQLAlchemy
- **Templating:** Jinja2
- **Frontend:** HTML, Bootstrap 4

## Prerequisites

- Python 3.10+
- PostgreSQL server
- pip

## Project Structure

```text
bootsrap2/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── .gitignore
├── static/
│   └── abc.mp4             # Background video for homepage
└── templates/
    ├── index.html
    ├── about.html
    ├── login.html
    ├── register.html
    ├── create_post.html
    ├── view_post.html
    ├── profile.html
    ├── post_success.html
    └── single_post.html
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/lavanyaboda17-svg/API.git
cd API
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

**Windows (PowerShell):**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL

Create a database and user matching the connection string in `app.py`:

```sql
CREATE USER lavanya WITH PASSWORD '123';
CREATE DATABASE post OWNER lavanya;
```

Create the required tables:

```sql
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
```

### 5. Run the application

```bash
python app.py
```

The app will be available at:

```text
http://127.0.0.1:5000
```

## Running with Docker

Build the image:

```bash
docker build -t website-app .
```

Run the container:

```bash
docker run -p 5000:5000 website-app
```

## Routes

| Route | Method | Description |
| ------ | ------ | ----------- |
| `/` | GET | Homepage |
| `/about` | GET | About page |
| `/register` | GET, POST | User registration |
| `/login` | GET, POST | User login |
| `/logout` | GET | Logout, clears session |
| `/post` | GET | Create post form (login required) |
| `/create-post` | POST | Submit a new post (login required) |
| `/user/<user_id>/posts` | GET | View a user's posts (login required) |
| `/user/profile/<user_id>` | GET | View user profile (login required) |