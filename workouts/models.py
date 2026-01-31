from django.db import models
from django.contrib.auth.models import User


class Exercise(models.Model):
    """Individual exercises that can be part of workouts"""
    
    CATEGORY_CHOICES = [
        ('cardio', 'Cardio'),
        ('strength', 'Strength'),
        ('flexibility', 'Flexibility'),
        ('balance', 'Balance'),
        ('plyometric', 'Plyometric'),
    ]
    
    MUSCLE_GROUP_CHOICES = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('shoulders', 'Shoulders'),
        ('arms', 'Arms'),
        ('legs', 'Legs'),
        ('core', 'Core'),
        ('full_body', 'Full Body'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    muscle_group = models.CharField(max_length=20, choices=MUSCLE_GROUP_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    
    # Media
    image = models.ImageField(upload_to='exercises/', null=True, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or video link")
    
    # Instructions
    instructions = models.TextField(help_text="Step-by-step instructions")
    tips = models.TextField(blank=True, help_text="Tips for proper form")
    
    # Equipment
    equipment_needed = models.CharField(max_length=200, blank=True, help_text="e.g., Dumbbells, Barbell, None")
    
    # Metrics
    calories_per_minute = models.DecimalField(max_digits=5, decimal_places=2, default=5.0, help_text="Estimated calories burned per minute")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Exercise"
        verbose_name_plural = "Exercises"


class Workout(models.Model):
    """Workout plans/routines"""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('strength', 'Strength'),
        ('endurance', 'Endurance'),
        ('flexibility', 'Flexibility'),
        ('general', 'General Fitness'),
    ]
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_workouts', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)
    
    # Details
    duration = models.IntegerField(help_text="Duration in minutes")
    estimated_calories = models.IntegerField(help_text="Estimated calories burned")
    
    # Media
    image = models.ImageField(upload_to='workouts/', null=True, blank=True)
    
    # Visibility
    is_public = models.BooleanField(default=True, help_text="Can other users see this workout?")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Workout"
        verbose_name_plural = "Workouts"


class WorkoutExercise(models.Model):
    """Junction table linking workouts to exercises with specific details"""
    
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='workout_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='workout_exercises')
    
    order = models.IntegerField(default=0, help_text="Order in the workout")
    
    # Exercise specifics for this workout
    sets = models.IntegerField(default=3)
    reps = models.IntegerField(null=True, blank=True, help_text="Number of reps (leave blank for time-based)")
    duration = models.IntegerField(null=True, blank=True, help_text="Duration in seconds (for cardio/timed exercises)")
    rest_time = models.IntegerField(default=60, help_text="Rest time in seconds between sets")
    
    notes = models.TextField(blank=True, help_text="Special instructions for this exercise in this workout")
    
    def __str__(self):
        return f"{self.workout.name} - {self.exercise.name}"
    
    class Meta:
        ordering = ['workout', 'order']
        unique_together = ['workout', 'exercise', 'order']
        verbose_name = "Workout Exercise"
        verbose_name_plural = "Workout Exercises"


class WorkoutSession(models.Model):
    """Track completed workout sessions"""
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name='sessions')
    
    # Session details
    scheduled_date = models.DateField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Performance
    duration_minutes = models.IntegerField(null=True, blank=True, help_text="Actual duration")
    calories_burned = models.IntegerField(null=True, blank=True, help_text="Actual calories burned")
    
    # Feedback
    difficulty_rating = models.IntegerField(null=True, blank=True, help_text="1-5 rating")
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.workout.name} on {self.scheduled_date}"
    
    class Meta:
        ordering = ['-scheduled_date']
        verbose_name = "Workout Session"
        verbose_name_plural = "Workout Sessions"


class ExerciseLog(models.Model):
    """Track performance for individual exercises within a workout session"""
    
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='exercise_logs')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='exercise_logs')
    
    # Performance data
    sets_completed = models.IntegerField(default=0)
    reps_completed = models.IntegerField(null=True, blank=True)
    weight_used = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Additional tracking
    notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.session.user.username} - {self.exercise.name}"
    
    class Meta:
        ordering = ['session', 'created_at']
        verbose_name = "Exercise Log"
        verbose_name_plural = "Exercise Logs"


class PersonalRecord(models.Model):
    """Track personal records/best performances"""
    
    RECORD_TYPE_CHOICES = [
        ('weight', 'Max Weight'),
        ('reps', 'Max Reps'),
        ('duration', 'Longest Duration'),
        ('distance', 'Longest Distance'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_records')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='personal_records')
    
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    value = models.DecimalField(max_digits=8, decimal_places=2, help_text="Record value")
    unit = models.CharField(max_length=20, help_text="e.g., kg, reps, seconds, km")
    
    achieved_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.name}: {self.value} {self.unit}"
    
    class Meta:
        ordering = ['-achieved_at']
        verbose_name = "Personal Record"
        verbose_name_plural = "Personal Records"
        unique_together = ['user', 'exercise', 'record_type']