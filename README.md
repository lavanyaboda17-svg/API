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

bootsrap2/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── init.sql                # Auto-creates users/posts tables on first Postgres run
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

If running Postgres via Docker (see below), tables are created automatically from `init.sql` — no manual step needed.

If running Postgres locally (without Docker), create the database/user and run `init.sql` manually:

```bash
psql -U postgres -c "CREATE USER lavanya WITH PASSWORD '123';"
psql -U postgres -c "CREATE DATABASE post OWNER lavanya;"
psql -U lavanya -d post -f init.sql
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

This project uses two containers: one for PostgreSQL (database) and one for the Flask app.

### 1. Start the PostgreSQL container

The `init.sql` file (in the project root) automatically creates the `users` and `posts` tables the first time the Postgres container starts.

**PowerShell:**
```powershell
docker run -d --name my-postgres -e POSTGRES_USER=lavanya -e POSTGRES_PASSWORD=123 -e POSTGRES_DB=post -p 5432:5432 -v "${PWD}\init.sql:/docker-entrypoint-initdb.d/init.sql" postgres
```

**CMD:**
```cmd
docker run -d --name my-postgres -e POSTGRES_USER=lavanya -e POSTGRES_PASSWORD=123 -e POSTGRES_DB=post -p 5432:5432 -v "%cd%\init.sql:/docker-entrypoint-initdb.d/init.sql" postgres
```

Verify the tables were created:
```bash
docker exec -it my-postgres psql -U lavanya -d post
\dt
```

### 2. Build the Flask app image

```bash
docker build -t website-app .
```

### 3. Run the Flask app container, connected to Postgres

```bash
docker run -d --name my-website -p 5000:5000 -e DB_HOST=my-postgres --link my-postgres website-app
```

`DB_HOST=my-postgres` tells the app to connect to the Postgres container by its container name instead of `localhost` (see `app.py`, which reads `DB_HOST` from the environment).

The app will be available at:
```text
http://localhost:5000
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