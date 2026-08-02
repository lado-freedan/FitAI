# 🏋️‍♂️ FitAI Backend Services

![Python (https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
![Django (https://img.shields.io/badge/Django-4.2+-green.svg)](https://www.djangoproject.com/)
![DRF (https://img.shields.io/badge/Django%20REST%20Framework-3.14+-red.svg)](https://www.django-rest-framework.org/)
![Docker (https://img.shields.io/badge/Docker-Containerized-blueviolet.svg)](https://www.docker.com/)
![Celery (https://img.shields.io/badge/Celery-Async%20Tasks-brightgreen.svg)](https://docs.celeryq.dev/)
![OpenAPI (https://img.shields.io/badge/Swagger-OpenAPI%203.0-green.svg)](http://localhost:8000/api/docs/)

FitAI is an asynchronous, high-performance RESTful API backend built with Django REST Framework, Celery, Redis, and Google Gemini Vision AI. It processes body metric photos asynchronously to deliver automated fitness and nutrition recommendations.

---

## 🚀 Key Features

*   JWT Authentication: Secure user registration, authentication, and token refreshing via djangorestframework-simplejwt.
*   Asynchronous AI Task Processing: Offloads heavy computer vision tasks (Gemini Vision API) to background workers using Celery and Redis.
*   OpenAPI 3.0 & Swagger UI: Interactive, real-time API documentation powered by drf-spectacular.
*   Containerized Architecture: Fully dockerized backend environment (web, celery_worker, redis, db).
*   User Tracking & Analytics: Dynamic tracking of daily logs, meal history, and weekly performance progress.

---

## 🛠️ Architecture & Tech Stack

*   Language & Core: Python 3.11+, Django, Django REST Framework
*   Task Queue & Caching: Celery, Redis
*   AI Service Integration: Google Gemini 1.5 Pro / Vision API
*   Containerization: Docker, Docker Compose
*   Database: PostgreSQL / SQLite (Development)
*   API Documentation: OpenAPI 3, Swagger UI (drf-spectacular)

---

## 🚥 API Endpoints Summary

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| POST | /api/users/register/ | Register a new user account | ❌ |
| POST | /api/users/login/ | Obtain JWT Access and Refresh Tokens | ❌ |
| POST | /api/users/token/refresh/ | Refresh expired Access Token | ❌ |
| GET | /api/users/me/ | Retrieve current authenticated profile | ✅ |
| PATCH| /api/users/profile/update/| Update user physical metrics | ✅ |
| POST | /api/users/body-analysis/upload/ | Upload photo & trigger async AI analysis task | ✅ |
| GET | /api/users/plans/latest/ | Check status/result of background AI plan generation | ✅ |
| GET | /api/users/plans/history/ | View historical fitness plans | ✅ |
| POST | /api/users/daily-log/ | Submit daily activity and meal log | ✅ |
| GET | /api/users/weekly-analysis/ | Fetch aggregated weekly insights | ✅ |
| POST | /api/users/generate-plan/ | Trigger manual AI fitness plan generation | ✅ |

---

## 🐳 Quick Start with Docker

### Prerequisites
Make sure you have Docker (https://www.docker.com/) and Docker Compose (https://docs.docker.com/compose/) installed on your machine.

### 1. Environment Setup
Create a .env file in the root directory:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True
GEMINI_API_KEY=your_google_gemini_api_key
REDIS_URL=redis://redis:6379/0