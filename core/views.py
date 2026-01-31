from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta, date
from .models import UserProfile, Goal, ProgressLog, Achievement
from workouts.models import WorkoutSession
from nutrition.models import NutritionLog


def home(request):
    """Home page view"""
    context = {
        'title': 'FitTrack - Home'
    }
    return render(request, 'core/home.html', context)


@login_required
def dashboard(request):
    """User dashboard with stats and overview"""
    user = request.user
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    # Get workout stats for this week
    workout_sessions = WorkoutSession.objects.filter(
        user=user,
        scheduled_date__gte=week_ago,
        scheduled_date__lte=today
    )
    
    workouts_completed = workout_sessions.filter(status='completed').count()
    workouts_planned = workout_sessions.count()
    workout_percentage = (workouts_completed / workouts_planned * 100) if workouts_planned > 0 else 0
    
    # Calculate calories burned this week
    calories_burned = workout_sessions.filter(
        status='completed'
    ).aggregate(total=Sum('calories_burned'))['total'] or 0
    
    # Active days (days with completed workouts)
    active_days = workout_sessions.filter(
        status='completed'
    ).values('scheduled_date').distinct().count()
    
    # Get active goals
    active_goals = Goal.objects.filter(user=user, status='active')
    
    # Get recent progress logs
    recent_progress = ProgressLog.objects.filter(user=user)[:5]
    
    # Get recent achievements
    recent_achievements = Achievement.objects.filter(user=user)[:3]
    
    context = {
        'title': 'Dashboard',
        'stats': {
            'workouts_completed': workouts_completed,
            'workouts_planned': workouts_planned,
            'workout_percentage': round(workout_percentage),
            'calories_burned': calories_burned,
            'active_days': active_days,
        },
        'active_goals': active_goals,
        'recent_progress': recent_progress,
        'recent_achievements': recent_achievements,
    }
    
    return render(request, 'core/dashboard.html', context)


@login_required
def profile(request):
    """User profile view"""
    profile = request.user.profile
    
    # Get all user goals
    goals = Goal.objects.filter(user=request.user)
    
    # Get progress logs
    progress_logs = ProgressLog.objects.filter(user=request.user)[:10]
    
    # Get achievements
    achievements = Achievement.objects.filter(user=request.user)
    
    context = {
        'title': 'Profile',
        'profile': profile,
        'goals': goals,
        'progress_logs': progress_logs,
        'achievements': achievements,
    }
    
    return render(request, 'core/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        # Update profile fields
        profile.date_of_birth = request.POST.get('date_of_birth')
        profile.gender = request.POST.get('gender')
        profile.height = request.POST.get('height')
        profile.current_weight = request.POST.get('current_weight')
        profile.activity_level = request.POST.get('activity_level')
        profile.bio = request.POST.get('bio')
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'title': 'Edit Profile',
        'profile': profile,
    }
    
    return render(request, 'core/edit_profile.html', context)


@login_required
def goals(request):
    """View all goals"""
    user_goals = Goal.objects.filter(user=request.user)
    
    context = {
        'title': 'My Goals',
        'goals': user_goals,
    }
    
    return render(request, 'core/goals.html', context)


@login_required
def create_goal(request):
    """Create a new goal"""
    if request.method == 'POST':
        goal = Goal.objects.create(
            user=request.user,
            goal_type=request.POST.get('goal_type'),
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            target_weight=request.POST.get('target_weight') or None,
            target_date=request.POST.get('target_date') or None,
        )
        messages.success(request, 'Goal created successfully!')
        return redirect('goals')
    
    context = {
        'title': 'Create Goal',
    }
    
    return render(request, 'core/create_goal.html', context)


@login_required
def update_goal(request, goal_id):
    """Update goal progress"""
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        goal.progress_percentage = request.POST.get('progress_percentage')
        goal.status = request.POST.get('status')
        
        if goal.status == 'completed':
            goal.completed_at = timezone.now()
        
        goal.save()
        messages.success(request, 'Goal updated successfully!')
        return redirect('goals')
    
    context = {
        'title': 'Update Goal',
        'goal': goal,
    }
    
    return render(request, 'core/update_goal.html', context)


@login_required
def progress(request):
    """View progress logs"""
    logs = ProgressLog.objects.filter(user=request.user)
    
    context = {
        'title': 'My Progress',
        'logs': logs,
    }
    
    return render(request, 'core/progress.html', context)


@login_required
def log_progress(request):
    """Log new progress entry"""
    if request.method == 'POST':
        progress_log = ProgressLog.objects.create(
            user=request.user,
            date=request.POST.get('date'),
            weight=request.POST.get('weight') or None,
            body_fat_percentage=request.POST.get('body_fat_percentage') or None,
            muscle_mass=request.POST.get('muscle_mass') or None,
            waist=request.POST.get('waist') or None,
            chest=request.POST.get('chest') or None,
            arms=request.POST.get('arms') or None,
            legs=request.POST.get('legs') or None,
            notes=request.POST.get('notes', ''),
        )
        
        # Handle photo upload
        if 'photo' in request.FILES:
            progress_log.photo = request.FILES['photo']
            progress_log.save()
        
        # Update current weight in profile
        if request.POST.get('weight'):
            profile = request.user.profile
            profile.current_weight = request.POST.get('weight')
            profile.save()
        
        messages.success(request, 'Progress logged successfully!')
        return redirect('progress')
    
    context = {
        'title': 'Log Progress',
        'today': date.today(),
    }
    
    return render(request, 'core/log_progress.html', context)


@login_required
def achievements(request):
    """View all achievements"""
    user_achievements = Achievement.objects.filter(user=request.user)
    
    context = {
        'title': 'My Achievements',
        'achievements': user_achievements,
    }
    
    return render(request, 'core/achievements.html', context)


# Authentication views
def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    context = {
        'title': 'Register',
        'form': form,
    }
    
    return render(request, 'core/register.html', context)


def user_login(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    context = {
        'title': 'Login',
    }
    
    return render(request, 'core/login.html', context)


@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')