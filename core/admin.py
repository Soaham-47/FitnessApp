from django.contrib import admin
from .models import UserProfile, Goal, ProgressLog, Achievement


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_weight', 'height', 'activity_level', 'created_at']
    list_filter = ['activity_level', 'gender', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Personal Info', {
            'fields': ('date_of_birth', 'gender', 'height', 'current_weight')
        }),
        ('Fitness Info', {
            'fields': ('activity_level',)
        }),
        ('Profile', {
            'fields': ('bio', 'profile_picture')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'goal_type', 'status', 'progress_percentage', 'target_date']
    list_filter = ['goal_type', 'status', 'created_at']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'goal_type', 'title', 'description')
        }),
        ('Targets', {
            'fields': ('target_weight', 'target_date')
        }),
        ('Progress', {
            'fields': ('status', 'progress_percentage')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProgressLog)
class ProgressLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'weight', 'body_fat_percentage', 'muscle_mass']
    list_filter = ['date', 'user']
    search_fields = ['user__username', 'notes']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'date')
        }),
        ('Body Measurements', {
            'fields': ('weight', 'body_fat_percentage', 'muscle_mass')
        }),
        ('Circumferences (cm)', {
            'fields': ('waist', 'chest', 'arms', 'legs')
        }),
        ('Additional', {
            'fields': ('notes', 'photo')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'achievement_type', 'icon', 'earned_at']
    list_filter = ['achievement_type', 'earned_at']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['earned_at']
    date_hierarchy = 'earned_at'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'achievement_type', 'title', 'icon')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamp', {
            'fields': ('earned_at',)
        }),
    )