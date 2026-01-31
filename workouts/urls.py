from django.urls import path
from . import views

urlpatterns = [
    # Workouts
    path('', views.workouts, name='workouts'),
    path('<int:workout_id>/', views.workout_detail, name='workout_detail'),
    path('create/', views.create_workout, name='create_workout'),
    path('<int:workout_id>/edit/', views.edit_workout, name='edit_workout'),
    path('<int:workout_id>/add-exercise/', views.add_exercise_to_workout, name='add_exercise_to_workout'),
    
    # Workout Sessions
    path('<int:workout_id>/start/', views.start_workout, name='start_workout'),
    path('session/<int:session_id>/', views.workout_session, name='workout_session'),
    path('session/<int:session_id>/exercise/<int:exercise_id>/log/', views.log_exercise, name='log_exercise'),
    path('session/<int:session_id>/complete/', views.complete_workout, name='complete_workout'),
    path('my-workouts/', views.my_workouts, name='my_workouts'),
    
    # Exercises
    path('exercises/', views.exercises, name='exercises'),
    path('exercises/<int:exercise_id>/', views.exercise_detail, name='exercise_detail'),
    
    # Personal Records
    path('personal-records/', views.personal_records, name='personal_records'),
]