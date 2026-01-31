from django.contrib import admin
from .models import (
    Recipe, MealPlan, MealPlanDay, MealPlanRecipe,
    NutritionLog, MealLog, FoodItem
)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'meal_type', 'difficulty', 'calories', 'protein', 'prep_time', 'cook_time', 'is_public']
    list_filter = ['meal_type', 'difficulty', 'is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_public']
    search_fields = ['name', 'description', 'ingredients', 'creator__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('creator', 'name', 'description', 'meal_type', 'difficulty')
        }),
        ('Nutrition (per serving)', {
            'fields': ('calories', 'protein', 'carbs', 'fats', 'fiber', 'servings')
        }),
        ('Timing', {
            'fields': ('prep_time', 'cook_time')
        }),
        ('Recipe Content', {
            'fields': ('ingredients', 'instructions', 'image')
        }),
        ('Dietary Tags', {
            'fields': ('is_vegetarian', 'is_vegan', 'is_gluten_free', 'is_dairy_free')
        }),
        ('Visibility', {
            'fields': ('is_public',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class MealPlanDayInline(admin.TabularInline):
    model = MealPlanDay
    extra = 0
    fields = ['day_number', 'notes']
    ordering = ['day_number']


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'plan_type', 'duration_days', 'daily_calories', 'is_public']
    list_filter = ['plan_type', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'creator__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MealPlanDayInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('creator', 'name', 'description', 'plan_type', 'duration_days')
        }),
        ('Daily Targets', {
            'fields': ('daily_calories', 'daily_protein', 'daily_carbs', 'daily_fats')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Visibility', {
            'fields': ('is_public',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class MealPlanRecipeInline(admin.TabularInline):
    model = MealPlanRecipe
    extra = 1
    fields = ['recipe', 'meal_time', 'servings', 'notes']


@admin.register(MealPlanDay)
class MealPlanDayAdmin(admin.ModelAdmin):
    list_display = ['meal_plan', 'day_number']
    list_filter = ['meal_plan']
    search_fields = ['meal_plan__name']
    inlines = [MealPlanRecipeInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('meal_plan', 'day_number')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(MealPlanRecipe)
class MealPlanRecipeAdmin(admin.ModelAdmin):
    list_display = ['meal_plan_day', 'recipe', 'meal_time', 'servings']
    list_filter = ['meal_time', 'meal_plan_day__meal_plan']
    search_fields = ['recipe__name', 'meal_plan_day__meal_plan__name']


class MealLogInline(admin.TabularInline):
    model = MealLog
    extra = 0
    fields = ['meal_type', 'meal_name', 'calories', 'protein', 'carbs', 'fats', 'servings']
    readonly_fields = ['created_at']


@admin.register(NutritionLog)
class NutritionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'total_calories', 'total_protein', 'total_carbs', 'total_fats', 'water_intake']
    list_filter = ['date', 'user']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    inlines = [MealLogInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'date')
        }),
        ('Daily Totals', {
            'fields': ('total_calories', 'total_protein', 'total_carbs', 'total_fats', 'total_fiber')
        }),
        ('Hydration', {
            'fields': ('water_intake',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display = ['nutrition_log', 'meal_type', 'meal_name', 'calories', 'protein', 'servings', 'time']
    list_filter = ['meal_type', 'nutrition_log__user', 'nutrition_log__date']
    search_fields = ['meal_name', 'nutrition_log__user__username']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('nutrition_log', 'recipe', 'meal_type', 'meal_name')
        }),
        ('Nutrition', {
            'fields': ('calories', 'protein', 'carbs', 'fats', 'servings')
        }),
        ('Details', {
            'fields': ('time', 'notes', 'photo')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'serving_size', 'calories', 'protein']
    list_filter = ['category', 'is_vegetarian', 'is_vegan']
    search_fields = ['name', 'brand']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category', 'brand', 'serving_size')
        }),
        ('Nutrition', {
            'fields': ('calories', 'protein', 'carbs', 'fats', 'fiber')
        }),
        ('Dietary Tags', {
            'fields': ('is_vegetarian', 'is_vegan')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )