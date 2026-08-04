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
- Forgot password / reset password via email
- Edit and delete posts
- Cloudinary-based image hosting

## Tech Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL
- **ORM:** Flask-SQLAlchemy
- **Templating:** Jinja2
- **Frontend:** HTML, Bootstrap 4
- **Image Hosting:** Cloudinary
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
    ├── forgot_password.html
    ├── reset_password.html
    ├── create_post.html
    ├── view_post.html
    ├── profile.html
    ├── post_found.html
    ├── post_not_found.html
    ├── head.html
    ├── header.html
    └── footer.html
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

MAIL_SERVER=your_mail_server
MAIL_PORT=your_mail_port
MAIL_USE_TLS=True
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_email_app_password

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
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
| `/forgot-password` | GET, POST | Request password reset link via email |
| `/reset-password/<token>` | GET, POST | Reset password using emailed token |
| `/post/<post_id>/edit` | GET, POST | Edit an existing post (login required) |
| `/post/<post_id>/delete` | POST | Delete a post (login required) |