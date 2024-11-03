# FastAPI Application

This is a FastAPI application with Docker and Nginx integration. The application includes features such as authentication, CRUD operations, and basic filtering capabilities.

## Features

- User registration, login, and JWT-based authentication
- CRUD operations on items, with user-specific access
- Pagination, filtering, and search capabilities on items
- Options to launch with docker-compose or dockerfile for easy deployment
- Reverse proxy with nginx

## Prerequisites

- **Docker** and **Docker Compose** should be installed.
- **Python 3.8+** (if running locally without Docker)

## Improvements

Introduce templates and static content for the front-end

## Getting Started

Create a .env file in the project root to store sensitive information, such as the database URL and JWT settings.

Default .env file contains the following information:
```commandline
DATABASE_URL=sqlite:///./db_data/database.db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

To start the application using Docker Compose, including Nginx as a reverse proxy:
```commandline
docker-compose up --build
```

Reach the generated interactive documentation under:

    Swagger UI: http://localhost/docs
    ReDoc: http://localhost/redoc

In case of local tests, first install requirements and then run tests
```commandline
pip install -r requirements.txt
pytest /tests
```

To run tests online on the container:
```commandline
docker-compose exec web pytest
```

Folder Structure

    app: Contains the FastAPI application code, including models, routes, and logic.
    nginx: Contains the Nginx configuration file (nginx.conf).
    db_data: Directory mounted for the SQLite database data.