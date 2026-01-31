from django.urls import path
from . import views

urlpatterns = [
    # Recipes/Meals
    path('', views.meals, name='meals'),
    path('<int:meal_id>/', views.meal_detail, name='meal_detail'),
    path('create/', views.create_recipe, name='create_recipe'),
    
    # Meal Plans
    path('plans/', views.meal_plans, name='meal_plans'),
    path('plans/<int:plan_id>/', views.meal_plan_detail, name='meal_plan_detail'),
    path('plans/create/', views.create_meal_plan, name='create_meal_plan'),
    path('plans/<int:plan_id>/edit/', views.edit_meal_plan, name='edit_meal_plan'),
    
    # Nutrition Logging
    path('log/', views.nutrition_log, name='nutrition_log'),
    path('log/add-meal/', views.add_meal_log, name='add_meal_log'),
    path('log/update-water/', views.update_water_intake, name='update_water_intake'),
    path('log/meal/<int:meal_log_id>/delete/', views.delete_meal_log, name='delete_meal_log'),
    
    # Statistics
    path('stats/', views.nutrition_stats, name='nutrition_stats'),
    
    # Food Database
    path('foods/', views.food_items, name='food_items'),
    path('foods/<int:item_id>/', views.food_item_detail, name='food_item_detail'),
]