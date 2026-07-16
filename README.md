# BlogApp

A simple Flask-based blogging application with user registration, login, and post creation features. Built with Flask, Flask-SQLAlchemy, and PostgreSQL.

## Features

- User registration with password hashing (Werkzeug security)
- User login with session-based authentication
- Session timeout (auto-logout after inactivity)
- Create and view blog posts
- User profile pages
- Logout functionality
- PostgreSQL Database
- Docker & Docker Compose Support

## Tech Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL
- **ORM:** Flask-SQLAlchemy
- **Templating:** Jinja2
- **Frontend:** HTML, Bootstrap 4
- **Containerization:** Docker, Docker Compose

## Prerequisites

- Python 3.10+
- PostgreSQL server (only needed for non-Docker local runs)
- pip
- Docker & Docker Compose (for containerized runs)

## Project Structure

```
BlogApp/
│
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── .env                     # Real credentials (not committed)
├── .env.example             # Template for .env
├── .dockerignore
├── .gitignore
├── static/
│   └── abc.mp4              # Background video for homepage
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

### 2. Configure environment variables

Copy the example file and fill in your own values:

```bash
cp .env.example .env
```

`.env` must contain:

```
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name

SECRET_KEY=your_secret_key
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

The application will be available at:

```
http://127.0.0.1:5000
```

---

## Run with Docker Compose

### Build the Docker images

```bash
docker compose build
```

### Start the containers

```bash
docker compose up
```

Run in detached mode:

```bash
docker compose up -d
```

### Stop the containers

```bash
docker compose stop
```

### Stop and remove the containers (data is preserved)

```bash
docker compose down
```

### Stop, remove containers, AND delete the database data

```bash
docker compose down -v
```

The application will be available at:

```
http://localhost:5000
```

The PostgreSQL database is exposed on the host at `localhost:5433` (mapped from the container's internal port `5432`), so external tools like pgAdmin should connect using port `5433`.

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