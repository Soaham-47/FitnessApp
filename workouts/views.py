from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date
from .models import (
    Exercise, Workout, WorkoutExercise, WorkoutSession, 
    ExerciseLog, PersonalRecord
)


@login_required
def workouts(request):
    """List all available workouts"""
    # Get public workouts and user's own workouts
    all_workouts = Workout.objects.filter(is_public=True) | Workout.objects.filter(creator=request.user)
    all_workouts = all_workouts.distinct()
    
    # Filter by difficulty if provided
    difficulty = request.GET.get('difficulty')
    if difficulty:
        all_workouts = all_workouts.filter(difficulty=difficulty)
    
    # Filter by goal if provided
    goal = request.GET.get('goal')
    if goal:
        all_workouts = all_workouts.filter(goal=goal)
    
    context = {
        'title': 'Workouts',
        'workouts': all_workouts,
    }
    
    return render(request, 'workouts/workouts.html', context)


@login_required
def workout_detail(request, workout_id):
    """View workout details"""
    workout = get_object_or_404(Workout, id=workout_id)
    
    # Get exercises in this workout
    workout_exercises = WorkoutExercise.objects.filter(workout=workout).select_related('exercise')
    
    # Get user's recent sessions with this workout
    recent_sessions = WorkoutSession.objects.filter(
        user=request.user,
        workout=workout
    )[:5]
    
    context = {
        'title': workout.name,
        'workout': workout,
        'workout_exercises': workout_exercises,
        'recent_sessions': recent_sessions,
    }
    
    return render(request, 'workouts/workout_detail.html', context)


@login_required
def create_workout(request):
    """Create a new workout"""
    if request.method == 'POST':
        workout = Workout.objects.create(
            creator=request.user,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            difficulty=request.POST.get('difficulty'),
            goal=request.POST.get('goal'),
            duration=request.POST.get('duration'),
            estimated_calories=request.POST.get('estimated_calories'),
            is_public=request.POST.get('is_public') == 'on',
        )
        
        # Handle image upload
        if 'image' in request.FILES:
            workout.image = request.FILES['image']
            workout.save()
        
        messages.success(request, 'Workout created successfully! Now add exercises.')
        return redirect('edit_workout', workout_id=workout.id)
    
    context = {
        'title': 'Create Workout',
    }
    
    return render(request, 'workouts/create_workout.html', context)


@login_required
def edit_workout(request, workout_id):
    """Edit workout and manage exercises"""
    workout = get_object_or_404(Workout, id=workout_id, creator=request.user)
    workout_exercises = WorkoutExercise.objects.filter(workout=workout).select_related('exercise')
    
    # Get all exercises for adding
    all_exercises = Exercise.objects.all()
    
    context = {
        'title': f'Edit {workout.name}',
        'workout': workout,
        'workout_exercises': workout_exercises,
        'all_exercises': all_exercises,
    }
    
    return render(request, 'workouts/edit_workout.html', context)


@login_required
def add_exercise_to_workout(request, workout_id):
    """Add exercise to workout"""
    if request.method == 'POST':
        workout = get_object_or_404(Workout, id=workout_id, creator=request.user)
        exercise = get_object_or_404(Exercise, id=request.POST.get('exercise_id'))
        
        WorkoutExercise.objects.create(
            workout=workout,
            exercise=exercise,
            order=request.POST.get('order', 0),
            sets=request.POST.get('sets', 3),
            reps=request.POST.get('reps') or None,
            duration=request.POST.get('duration') or None,
            rest_time=request.POST.get('rest_time', 60),
            notes=request.POST.get('notes', ''),
        )
        
        messages.success(request, f'{exercise.name} added to workout!')
        return redirect('edit_workout', workout_id=workout_id)
    
    return redirect('workouts')


@login_required
def start_workout(request, workout_id):
    """Start a workout session"""
    workout = get_object_or_404(Workout, id=workout_id)
    
    # Create a new workout session
    session = WorkoutSession.objects.create(
        user=request.user,
        workout=workout,
        scheduled_date=date.today(),
        started_at=timezone.now(),
        status='in_progress',
    )
    
    messages.success(request, f'Workout "{workout.name}" started!')
    return redirect('workout_session', session_id=session.id)


@login_required
def workout_session(request, session_id):
    """Active workout session view"""
    session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
    workout_exercises = WorkoutExercise.objects.filter(workout=session.workout).select_related('exercise')
    
    # Get existing exercise logs for this session
    exercise_logs = ExerciseLog.objects.filter(session=session)
    
    context = {
        'title': f'Session: {session.workout.name}',
        'session': session,
        'workout_exercises': workout_exercises,
        'exercise_logs': exercise_logs,
    }
    
    return render(request, 'workouts/workout_session.html', context)


@login_required
def log_exercise(request, session_id, exercise_id):
    """Log exercise performance during workout"""
    if request.method == 'POST':
        session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
        exercise = get_object_or_404(Exercise, id=exercise_id)
        
        # Create or update exercise log
        exercise_log, created = ExerciseLog.objects.get_or_create(
            session=session,
            exercise=exercise,
            defaults={
                'sets_completed': request.POST.get('sets_completed', 0),
                'reps_completed': request.POST.get('reps_completed') or None,
                'weight_used': request.POST.get('weight_used') or None,
                'duration_seconds': request.POST.get('duration_seconds') or None,
                'notes': request.POST.get('notes', ''),
                'completed': True,
            }
        )
        
        if not created:
            # Update existing log
            exercise_log.sets_completed = request.POST.get('sets_completed', 0)
            exercise_log.reps_completed = request.POST.get('reps_completed') or None
            exercise_log.weight_used = request.POST.get('weight_used') or None
            exercise_log.duration_seconds = request.POST.get('duration_seconds') or None
            exercise_log.notes = request.POST.get('notes', '')
            exercise_log.completed = True
            exercise_log.save()
        
        # Check for personal record
        if exercise_log.weight_used:
            pr, created = PersonalRecord.objects.get_or_create(
                user=request.user,
                exercise=exercise,
                record_type='weight',
                defaults={
                    'value': exercise_log.weight_used,
                    'unit': 'kg',
                }
            )
            if not created and exercise_log.weight_used > pr.value:
                pr.value = exercise_log.weight_used
                pr.save()
                messages.success(request, f'New personal record for {exercise.name}! 🎉')
        
        messages.success(request, f'{exercise.name} logged!')
        return redirect('workout_session', session_id=session_id)
    
    return redirect('workouts')


@login_required
def complete_workout(request, session_id):
    """Complete a workout session"""
    session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
    
    if request.method == 'POST':
        session.completed_at = timezone.now()
        session.status = 'completed'
        session.duration_minutes = request.POST.get('duration_minutes')
        session.calories_burned = request.POST.get('calories_burned')
        session.difficulty_rating = request.POST.get('difficulty_rating')
        session.notes = request.POST.get('notes', '')
        session.save()
        
        messages.success(request, 'Workout completed! Great job! 💪')
        return redirect('dashboard')
    
    context = {
        'title': 'Complete Workout',
        'session': session,
    }
    
    return render(request, 'workouts/complete_workout.html', context)


@login_required
def my_workouts(request):
    """View user's workout history"""
    sessions = WorkoutSession.objects.filter(user=request.user).select_related('workout')
    
    context = {
        'title': 'My Workout History',
        'sessions': sessions,
    }
    
    return render(request, 'workouts/my_workouts.html', context)


@login_required
def exercises(request):
    """List all exercises"""
    all_exercises = Exercise.objects.all()
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        all_exercises = all_exercises.filter(category=category)
    
    # Filter by muscle group if provided
    muscle_group = request.GET.get('muscle_group')
    if muscle_group:
        all_exercises = all_exercises.filter(muscle_group=muscle_group)
    
    context = {
        'title': 'Exercises',
        'exercises': all_exercises,
    }
    
    return render(request, 'workouts/exercises.html', context)


@login_required
def exercise_detail(request, exercise_id):
    """View exercise details"""
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    # Get user's personal record for this exercise
    try:
        pr = PersonalRecord.objects.get(
            user=request.user,
            exercise=exercise,
            record_type='weight'
        )
    except PersonalRecord.DoesNotExist:
        pr = None
    
    # Get recent logs for this exercise
    recent_logs = ExerciseLog.objects.filter(
        session__user=request.user,
        exercise=exercise
    ).select_related('session')[:10]
    
    context = {
        'title': exercise.name,
        'exercise': exercise,
        'personal_record': pr,
        'recent_logs': recent_logs,
    }
    
    return render(request, 'workouts/exercise_detail.html', context)


@login_required
def personal_records(request):
    """View all personal records"""
    records = PersonalRecord.objects.filter(user=request.user).select_related('exercise')
    
    context = {
        'title': 'Personal Records',
        'records': records,
    }
    
    return render(request, 'workouts/personal_records.html', context)