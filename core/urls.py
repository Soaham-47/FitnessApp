from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Goals
    path('goals/', views.goals, name='goals'),
    path('goals/create/', views.create_goal, name='create_goal'),
    path('goals/<int:goal_id>/update/', views.update_goal, name='update_goal'),
    
    # Progress
    path('progress/', views.progress, name='progress'),
    path('progress/log/', views.log_progress, name='log_progress'),
    
    # Achievements
    path('achievements/', views.achievements, name='achievements'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]