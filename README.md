# MyHaki Backend

## Overview
MyHaki is an AI-driven legal aid management system designed to streamline coordination between lawyers, families of pretrial detainees, and the Law Society of Kenya (LSK). The backend, built with Django REST Framework, provides secure API endpoints for user management, case applications, verification, assignment, tracking, and CPD points tracking. The platform leverages AI to classify and prioritize cases, enabling automated matching and assignment of lawyers to cases for efficient and transparent access to justice.

## Features
- User registration, login, and authentication
- CRUD operations for users, case applications, verification, assignment, tracking, and reporting
- Modular architecture for easy extension and maintainability
- Role-based access control for lawyers, LSK administrators, and detainee families
- Secure endpoints protected with token-based authentication
- AI-powered case classification, prioritization, and automated lawyer assignment
- CPD points tracking for lawyers participating in pro bono services
- Monthly analytics and reports for LSK oversight
- API documentation with Swagger UI

## Technology Stack
- Python 3.10+
- Django 4.2+
- Django REST Framework
- drf-yasg (Swagger API docs)
- PostgreSQL
- Token authentication (via DRF)
- Android (mobile clients for detainees/families and lawyers)
- Progressive Web App (for LSK admins)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Virtual environment tool
- PostgreSQL database

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/akirachix/myhaki-backend.git
   cd myhaki-backend
   ```

2. **Create and activate a virtual environment:**
   **Linux/macOS:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
   **Windows:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables and update `settings.py`:**
   - Configure your database connection, secret key, and any external API keys (if applicable).
   - Copy `.env.example` to `.env` and fill in your settings.

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser for admin access:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

8. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

## API Documentation

- **Swagger UI:** [https://myhaki-3e53581dd62e.herokuapp.com/swagger/](https://myhaki-3e53581dd62e.herokuapp.com/swagger/)
- **Redoc:** [https://myhaki-3e53581dd62e.herokuapp.com/redoc/](https://myhaki-3e53581dd62e.herokuapp.com/redoc/)

## Usage

- Endpoints for user registration, authentication, case applications, assignment, tracking, and reporting are accessible via the API.
- Mobile apps for detainees/families and lawyers communicate with the backend using secure REST endpoints.
- Role-based access ensures only authorized users can access sensitive data and operations.

## Contribution & Contacts

- For questions, issues, or contributions, please open an issue or discussion in this repository.
- Core team: Yordanos Hagos, Fiona Wesonga, Mahder Belete, Saloi Akeza, Lwam Bisrat

---
