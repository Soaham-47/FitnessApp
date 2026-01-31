# Fitness Tracking Web App

A full-stack fitness tracking platform built using Django that allows users to log workouts, track progress, and manage fitness goals.

## Features
- User authentication (signup/login)
- Log daily workouts and exercises
- Track fitness goals
- View workout history
- Upload and manage profile images
- Responsive UI using HTML/CSS

## Tech Stack
- Backend: Django
- Database: SQLite (can be replaced with PostgreSQL)
- Frontend: HTML, CSS
- Image Processing: Pillow
- Tools: Git

## System Design
The application follows Django’s MVT architecture.  
Users interact with views that handle requests, store data in relational models, and render dynamic templates.

The system consists of multiple Django apps with separate models for users, workouts, and goals, ensuring modularity and scalability.

## User Flow
1. User signs up or logs in.
2. User adds workouts and exercises.
3. User sets fitness goals.
4. User views workout history and progress over time.

## How to Run Locally
```bash
git clone https://github.com/Soaham-47/FitnessApp
cd FitnessApp
pip install -r requirements.txt
python manage.py runserver
