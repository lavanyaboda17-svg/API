# BlogApp

A simple Flask-based blogging application with user registration, login, and post creation features. Built with Flask, Flask-SQLAlchemy, and PostgreSQL. Organized using Flask Blueprints for modular structure.

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
- Paginated post listing (numbered pagination)
- Lazy-loaded images with fade-in effect

## Tech Stack

- **Backend:** Python, Flask, Flask-Blueprints
- **Architecture:** Modular Blueprint-based structure (`main`, `auth`, `posts`, `profile`)
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
├── extensions.py
├── utils.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── .env # Real credentials (not committed)
├── .env.example # Template for .env
├── .dockerignore
├── .gitignore
│
├── main/
│ ├── init.py
│ └── routes.py
│
├── auth/
│ ├── init.py
│ └── routes.py
│├── posts/
│ ├── init.py
│ └── routes.py
│
├── profile/
│ ├── init.py
│ └── routes.py
│
├── static/
│ └── abc.mp4 # Background video for homepage
│└── templates/
├── head.html
├── header.html
├── footer.html
├── main/
│ ├── index.html
│ └── about.html
├── auth/
│ ├── login.html
│ ├── register.html
│ ├── forgot_password.html
│ └── reset_password.html
├── posts/
│ ├── create_post.html
│ ├── view_post.html
│ └── single_post.html
└── profile/
└── profile.html

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

| Route | Method | Blueprint | Description |
| ------ | ------ | ------ | ----------- |
| `/` | GET | main | Homepage |
| `/about` | GET | main | About page |
| `/register` | GET, POST | auth | User registration |
| `/login` | GET, POST | auth | User login |
| `/logout` | GET | auth | Logout, clears session |
| `/forgot-password` | GET, POST | auth | Request password reset link via email |
| `/reset-password/<token>` | GET, POST | auth | Reset password using emailed token |
| `/post` | GET | posts | Create post form (login required) |
| `/create-post` | POST | posts | Submit a new post (login required) |
| `/user/<user_id>/posts` | GET | posts | View a user's posts, paginated (login required) |
| `/post/<post_id>` | GET | posts | View a single post (login required) |
| `/post/<post_id>/edit` | GET, POST | posts | Edit an existing post (login required) |
| `/post/<post_id>/delete` | POST | posts | Delete a post (login required) |
| `/user/profile/<user_id>` | GET | profile | View user profile (login required) |