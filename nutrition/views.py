from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import date, timedelta
from .models import (
    Recipe, MealPlan, MealPlanDay, MealPlanRecipe,
    NutritionLog, MealLog, FoodItem
)


@login_required
def meals(request):
    """List all available recipes/meals"""
    # Get public recipes and user's own recipes
    all_recipes = Recipe.objects.filter(is_public=True) | Recipe.objects.filter(creator=request.user)
    all_recipes = all_recipes.distinct()
    
    # Filter by meal type if provided
    meal_type = request.GET.get('meal_type')
    if meal_type:
        all_recipes = all_recipes.filter(meal_type=meal_type)
    
    # Filter by dietary preferences
    if request.GET.get('vegetarian') == 'on':
        all_recipes = all_recipes.filter(is_vegetarian=True)
    if request.GET.get('vegan') == 'on':
        all_recipes = all_recipes.filter(is_vegan=True)
    if request.GET.get('gluten_free') == 'on':
        all_recipes = all_recipes.filter(is_gluten_free=True)
    
    context = {
        'title': 'Meals',
        'meals': all_recipes,
    }
    
    return render(request, 'nutrition/meals.html', context)


@login_required
def meal_detail(request, meal_id):
    """View recipe/meal details"""
    recipe = get_object_or_404(Recipe, id=meal_id)
    
    # Parse ingredients into a list
    ingredients_list = recipe.ingredients.split('\n')
    
    # Parse instructions into steps
    instructions_list = recipe.instructions.split('\n')
    
    context = {
        'title': recipe.name,
        'meal': recipe,
        'ingredients_list': ingredients_list,
        'instructions_list': instructions_list,
    }
    
    return render(request, 'nutrition/meal_detail.html', context)


@login_required
def create_recipe(request):
    """Create a new recipe"""
    if request.method == 'POST':
        recipe = Recipe.objects.create(
            creator=request.user,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            meal_type=request.POST.get('meal_type'),
            difficulty=request.POST.get('difficulty', 'easy'),
            calories=request.POST.get('calories'),
            protein=request.POST.get('protein'),
            carbs=request.POST.get('carbs'),
            fats=request.POST.get('fats'),
            fiber=request.POST.get('fiber') or None,
            servings=request.POST.get('servings', 1),
            prep_time=request.POST.get('prep_time'),
            cook_time=request.POST.get('cook_time'),
            ingredients=request.POST.get('ingredients'),
            instructions=request.POST.get('instructions'),
            is_vegetarian=request.POST.get('is_vegetarian') == 'on',
            is_vegan=request.POST.get('is_vegan') == 'on',
            is_gluten_free=request.POST.get('is_gluten_free') == 'on',
            is_dairy_free=request.POST.get('is_dairy_free') == 'on',
            is_public=request.POST.get('is_public') == 'on',
        )
        
        # Handle image upload
        if 'image' in request.FILES:
            recipe.image = request.FILES['image']
            recipe.save()
        
        messages.success(request, 'Recipe created successfully!')
        return redirect('meal_detail', meal_id=recipe.id)
    
    context = {
        'title': 'Create Recipe',
    }
    
    return render(request, 'nutrition/create_recipe.html', context)


@login_required
def meal_plans(request):
    """List all meal plans"""
    # Get public meal plans and user's own meal plans
    all_plans = MealPlan.objects.filter(is_public=True) | MealPlan.objects.filter(creator=request.user)
    all_plans = all_plans.distinct()
    
    # Filter by plan type if provided
    plan_type = request.GET.get('plan_type')
    if plan_type:
        all_plans = all_plans.filter(plan_type=plan_type)
    
    context = {
        'title': 'Meal Plans',
        'meal_plans': all_plans,
    }
    
    return render(request, 'nutrition/meal_plans.html', context)


@login_required
def meal_plan_detail(request, plan_id):
    """View meal plan details"""
    meal_plan = get_object_or_404(MealPlan, id=plan_id)
    
    # Get all days for this meal plan with their recipes
    days = MealPlanDay.objects.filter(meal_plan=meal_plan).prefetch_related(
        'recipes__recipe'
    )
    
    context = {
        'title': meal_plan.name,
        'meal_plan': meal_plan,
        'days': days,
    }
    
    return render(request, 'nutrition/meal_plan_detail.html', context)


@login_required
def create_meal_plan(request):
    """Create a new meal plan"""
    if request.method == 'POST':
        meal_plan = MealPlan.objects.create(
            creator=request.user,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            plan_type=request.POST.get('plan_type'),
            duration_days=request.POST.get('duration_days', 7),
            daily_calories=request.POST.get('daily_calories'),
            daily_protein=request.POST.get('daily_protein'),
            daily_carbs=request.POST.get('daily_carbs'),
            daily_fats=request.POST.get('daily_fats'),
            is_public=request.POST.get('is_public') == 'on',
        )
        
        # Handle image upload
        if 'image' in request.FILES:
            meal_plan.image = request.FILES['image']
            meal_plan.save()
        
        # Create days for this meal plan
        for day_num in range(1, int(meal_plan.duration_days) + 1):
            MealPlanDay.objects.create(
                meal_plan=meal_plan,
                day_number=day_num
            )
        
        messages.success(request, 'Meal plan created! Now add meals to each day.')
        return redirect('edit_meal_plan', plan_id=meal_plan.id)
    
    context = {
        'title': 'Create Meal Plan',
    }
    
    return render(request, 'nutrition/create_meal_plan.html', context)


@login_required
def edit_meal_plan(request, plan_id):
    """Edit meal plan"""
    meal_plan = get_object_or_404(MealPlan, id=plan_id, creator=request.user)
    days = MealPlanDay.objects.filter(meal_plan=meal_plan).prefetch_related('recipes__recipe')
    all_recipes = Recipe.objects.filter(is_public=True) | Recipe.objects.filter(creator=request.user)
    
    context = {
        'title': f'Edit {meal_plan.name}',
        'meal_plan': meal_plan,
        'days': days,
        'all_recipes': all_recipes,
    }
    
    return render(request, 'nutrition/edit_meal_plan.html', context)


@login_required
def nutrition_log(request):
    """View nutrition log"""
    # Get date from query params or default to today
    log_date = request.GET.get('date', date.today())
    if isinstance(log_date, str):
        from datetime import datetime
        log_date = datetime.strptime(log_date, '%Y-%m-%d').date()
    
    # Get or create nutrition log for this date
    log, created = NutritionLog.objects.get_or_create(
        user=request.user,
        date=log_date
    )
    
    # Get all meals for this log
    meals = MealLog.objects.filter(nutrition_log=log)
    
    # Calculate totals from meals
    totals = meals.aggregate(
        total_calories=Sum('calories'),
        total_protein=Sum('protein'),
        total_carbs=Sum('carbs'),
        total_fats=Sum('fats'),
    )
    
    # Update log totals
    log.total_calories = totals['total_calories'] or 0
    log.total_protein = totals['total_protein'] or 0
    log.total_carbs = totals['total_carbs'] or 0
    log.total_fats = totals['total_fats'] or 0
    log.save()
    
    # Get previous and next dates for navigation
    prev_date = log_date - timedelta(days=1)
    next_date = log_date + timedelta(days=1)
    
    context = {
        'title': f'Nutrition Log - {log_date}',
        'log': log,
        'meals': meals,
        'log_date': log_date,
        'prev_date': prev_date,
        'next_date': next_date,
    }
    
    return render(request, 'nutrition/nutrition_log.html', context)


@login_required
def add_meal_log(request):
    """Add a meal to nutrition log"""
    if request.method == 'POST':
        log_date = request.POST.get('date', date.today())
        
        # Get or create nutrition log
        log, created = NutritionLog.objects.get_or_create(
            user=request.user,
            date=log_date
        )
        
        # Get recipe if provided
        recipe_id = request.POST.get('recipe_id')
        recipe = None
        if recipe_id:
            recipe = get_object_or_404(Recipe, id=recipe_id)
        
        # Create meal log
        servings = float(request.POST.get('servings', 1))
        
        if recipe:
            # Calculate nutrition based on servings
            meal_log = MealLog.objects.create(
                nutrition_log=log,
                recipe=recipe,
                meal_type=request.POST.get('meal_type'),
                meal_name=recipe.name,
                calories=int(recipe.calories * servings),
                protein=recipe.protein * servings,
                carbs=recipe.carbs * servings,
                fats=recipe.fats * servings,
                servings=servings,
                time=request.POST.get('time') or None,
                notes=request.POST.get('notes', ''),
            )
        else:
            # Manual entry
            meal_log = MealLog.objects.create(
                nutrition_log=log,
                meal_type=request.POST.get('meal_type'),
                meal_name=request.POST.get('meal_name'),
                calories=request.POST.get('calories'),
                protein=request.POST.get('protein'),
                carbs=request.POST.get('carbs'),
                fats=request.POST.get('fats'),
                servings=servings,
                time=request.POST.get('time') or None,
                notes=request.POST.get('notes', ''),
            )
        
        # Handle photo upload
        if 'photo' in request.FILES:
            meal_log.photo = request.FILES['photo']
            meal_log.save()
        
        messages.success(request, 'Meal logged successfully!')
        return redirect('nutrition_log')
    
    # Get available recipes for the form
    recipes = Recipe.objects.filter(is_public=True) | Recipe.objects.filter(creator=request.user)
    
    context = {
        'title': 'Add Meal',
        'recipes': recipes,
        'today': date.today(),
    }
    
    return render(request, 'nutrition/add_meal_log.html', context)


@login_required
def update_water_intake(request):
    """Update water intake for today"""
    if request.method == 'POST':
        log_date = request.POST.get('date', date.today())
        
        log, created = NutritionLog.objects.get_or_create(
            user=request.user,
            date=log_date
        )
        
        log.water_intake = request.POST.get('water_intake', 0)
        log.save()
        
        messages.success(request, 'Water intake updated!')
        return redirect('nutrition_log')
    
    return redirect('nutrition_log')


@login_required
def delete_meal_log(request, meal_log_id):
    """Delete a meal log entry"""
    meal_log = get_object_or_404(MealLog, id=meal_log_id, nutrition_log__user=request.user)
    meal_log.delete()
    messages.success(request, 'Meal deleted!')
    return redirect('nutrition_log')


@login_required
def nutrition_stats(request):
    """View nutrition statistics and trends"""
    # Get logs for the past 30 days
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    
    logs = NutritionLog.objects.filter(
        user=request.user,
        date__gte=thirty_days_ago,
        date__lte=today
    )
    
    # Calculate averages
    averages = logs.aggregate(
        avg_calories=Sum('total_calories') / logs.count() if logs.count() > 0 else 0,
        avg_protein=Sum('total_protein') / logs.count() if logs.count() > 0 else 0,
        avg_carbs=Sum('total_carbs') / logs.count() if logs.count() > 0 else 0,
        avg_fats=Sum('total_fats') / logs.count() if logs.count() > 0 else 0,
        avg_water=Sum('water_intake') / logs.count() if logs.count() > 0 else 0,
    )
    
    context = {
        'title': 'Nutrition Statistics',
        'logs': logs,
        'averages': averages,
    }
    
    return render(request, 'nutrition/nutrition_stats.html', context)


@login_required
def food_items(request):
    """List all food items"""
    items = FoodItem.objects.all()
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)
    
    # Search
    search = request.GET.get('search')
    if search:
        items = items.filter(name__icontains=search)
    
    context = {
        'title': 'Food Database',
        'food_items': items,
    }
    
    return render(request, 'nutrition/food_items.html', context)


@login_required
def food_item_detail(request, item_id):
    """View food item details"""
    item = get_object_or_404(FoodItem, id=item_id)
    
    context = {
        'title': item.name,
        'food_item': item,
    }
    
    return render(request, 'nutrition/food_item_detail.html', context)