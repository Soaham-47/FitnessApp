from django.contrib import admin
from .models import (
    Exercise, Workout, WorkoutExercise, WorkoutSession,
    ExerciseLog, PersonalRecord
)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'muscle_group', 'difficulty', 'equipment_needed']
    list_filter = ['category', 'muscle_group', 'difficulty']
    search_fields = ['name', 'description', 'instructions']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'category', 'muscle_group', 'difficulty')
        }),
        ('Details', {
            'fields': ('instructions', 'tips', 'equipment_needed', 'calories_per_minute')
        }),
        ('Media', {
            'fields': ('image', 'video_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1
    fields = ['exercise', 'order', 'sets', 'reps', 'duration', 'rest_time', 'notes']
    ordering = ['order']


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'difficulty', 'goal', 'duration', 'estimated_calories', 'is_public']
    list_filter = ['difficulty', 'goal', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'creator__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [WorkoutExerciseInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('creator', 'name', 'description', 'difficulty', 'goal')
        }),
        ('Details', {
            'fields': ('duration', 'estimated_calories', 'image')
        }),
        ('Visibility', {
            'fields': ('is_public',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ['workout', 'exercise', 'order', 'sets', 'reps', 'duration']
    list_filter = ['workout', 'exercise']
    search_fields = ['workout__name', 'exercise__name']
    ordering = ['workout', 'order']


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout', 'scheduled_date', 'status', 'duration_minutes', 'calories_burned']
    list_filter = ['status', 'scheduled_date', 'user']
    search_fields = ['user__username', 'workout__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'workout', 'scheduled_date', 'status')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration_minutes')
        }),
        ('Performance', {
            'fields': ('calories_burned', 'difficulty_rating')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExerciseLog)
class ExerciseLogAdmin(admin.ModelAdmin):
    list_display = ['session', 'exercise', 'sets_completed', 'reps_completed', 'weight_used', 'completed']
    list_filter = ['completed', 'exercise', 'session__user']
    search_fields = ['session__user__username', 'exercise__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('session', 'exercise', 'completed')
        }),
        ('Performance', {
            'fields': ('sets_completed', 'reps_completed', 'weight_used', 'duration_seconds')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PersonalRecord)
class PersonalRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'record_type', 'value', 'unit', 'achieved_at']
    list_filter = ['record_type', 'exercise', 'user']
    search_fields = ['user__username', 'exercise__name']
    readonly_fields = ['achieved_at']
    date_hierarchy = 'achieved_at'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'exercise', 'record_type')
        }),
        ('Record', {
            'fields': ('value', 'unit')
        }),
        ('Details', {
            'fields': ('notes', 'achieved_at')
        }),
    )