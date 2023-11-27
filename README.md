# Django Listing Reservation App


## Overview

The Django Listing Reservation App is a web application that allows users to create listings, reserve rooms, and provides listing owners with an overview of reservations. It is built with Django and Django Rest Framework, utilizing PostgreSQL for the database, Redis for caching, and Docker for containerization.

## Features

- **User Roles:**
  - **Listing Owner:** Can create and manage listings.
  - **User:** Can search for available rooms and make reservations.

- **Reservation System:**
  - Users can select date ranges to find available rooms.
  - Book rooms by providing necessary details.

- **Reporting:**
  - Listing owners can view reports in HTML format.

- **API Documentation:**
  - Utilizes Swagger for clear API documentation.

- **Styling:**
  - Uses Bootstrap for a clean and responsive user interface.

## Tech Stack

- Django 4.2.7
- Django Rest Framework 3.14.0
- PostgreSQL  (version)
- Redis 5.0.1
- Docker

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/django-listing-reservation.git
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run migrations:**
    ```bash
    python manage.py migrate
    ```

4. **Start the development server:**
    ```bash
    python manage.py runserver
    ```

5. **Access the application:**
    - Open your web browser and go to [http://localhost:8000](http://localhost:8000)

## API Documentation

- Access the Swagger documentation at [http://localhost:8000/swagger/](http://localhost:8000/swagger/)

## Configuration

- Configure the database settings in `settings.py`.
- Update Redis configurations in `settings.py`.

## Caching

- Redis is used for caching. Make sure your Redis server is running.

## Logging

- Django logger system is implemented. Check logs using Django's logging configuration.

## Docker

- Dockerized for easy deployment. Use the following commands:

    ```bash
    docker-compose build
    docker-compose up
    ```