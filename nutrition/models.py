from django.db import models
from django.contrib.auth.models import User


class Recipe(models.Model):
    """Individual recipes/meals"""
    
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('post_workout', 'Post-Workout'),
        ('pre_workout', 'Pre-Workout'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_recipes', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='easy')
    
    # Nutrition info (per serving)
    calories = models.IntegerField(help_text="Calories per serving")
    protein = models.DecimalField(max_digits=6, decimal_places=1, help_text="Protein in grams")
    carbs = models.DecimalField(max_digits=6, decimal_places=1, help_text="Carbohydrates in grams")
    fats = models.DecimalField(max_digits=6, decimal_places=1, help_text="Fats in grams")
    fiber = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="Fiber in grams")
    
    # Recipe details
    servings = models.IntegerField(default=1, help_text="Number of servings")
    prep_time = models.IntegerField(help_text="Preparation time in minutes")
    cook_time = models.IntegerField(help_text="Cooking time in minutes")
    
    # Content
    ingredients = models.TextField(help_text="List of ingredients (one per line)")
    instructions = models.TextField(help_text="Step-by-step cooking instructions")
    
    # Media
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    
    # Tags and filters
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    is_dairy_free = models.BooleanField(default=False)
    
    # Visibility
    is_public = models.BooleanField(default=True, help_text="Can other users see this recipe?")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def total_time(self):
        """Total time to prepare and cook"""
        return self.prep_time + self.cook_time
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"


class MealPlan(models.Model):
    """Weekly or daily meal plans"""
    
    PLAN_TYPE_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance'),
        ('keto', 'Keto'),
        ('low_carb', 'Low Carb'),
        ('high_protein', 'High Protein'),
        ('balanced', 'Balanced'),
    ]
    
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meal_plans', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    
    # Duration
    duration_days = models.IntegerField(default=7, help_text="Duration in days (e.g., 7 for weekly)")
    
    # Daily targets
    daily_calories = models.IntegerField(help_text="Target daily calories")
    daily_protein = models.DecimalField(max_digits=6, decimal_places=1, help_text="Target daily protein in grams")
    daily_carbs = models.DecimalField(max_digits=6, decimal_places=1, help_text="Target daily carbs in grams")
    daily_fats = models.DecimalField(max_digits=6, decimal_places=1, help_text="Target daily fats in grams")
    
    # Media
    image = models.ImageField(upload_to='meal_plans/', null=True, blank=True)
    
    # Visibility
    is_public = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Meal Plan"
        verbose_name_plural = "Meal Plans"


class MealPlanDay(models.Model):
    """Individual day within a meal plan"""
    
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='days')
    day_number = models.IntegerField(help_text="Day number in the plan (1-7 for weekly)")
    notes = models.TextField(blank=True, help_text="Special notes for this day")
    
    def __str__(self):
        return f"{self.meal_plan.name} - Day {self.day_number}"
    
    class Meta:
        ordering = ['meal_plan', 'day_number']
        unique_together = ['meal_plan', 'day_number']
        verbose_name = "Meal Plan Day"
        verbose_name_plural = "Meal Plan Days"


class MealPlanRecipe(models.Model):
    """Links recipes to specific days and meal times in a meal plan"""
    
    MEAL_TIME_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('morning_snack', 'Morning Snack'),
        ('lunch', 'Lunch'),
        ('afternoon_snack', 'Afternoon Snack'),
        ('dinner', 'Dinner'),
        ('evening_snack', 'Evening Snack'),
    ]
    
    meal_plan_day = models.ForeignKey(MealPlanDay, on_delete=models.CASCADE, related_name='recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='meal_plan_recipes')
    meal_time = models.CharField(max_length=20, choices=MEAL_TIME_CHOICES)
    servings = models.DecimalField(max_digits=4, decimal_places=1, default=1.0, help_text="Number of servings")
    
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.meal_plan_day} - {self.meal_time}: {self.recipe.name}"
    
    class Meta:
        ordering = ['meal_plan_day', 'meal_time']
        verbose_name = "Meal Plan Recipe"
        verbose_name_plural = "Meal Plan Recipes"


class NutritionLog(models.Model):
    """Daily nutrition tracking"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_logs')
    date = models.DateField()
    
    # Daily totals
    total_calories = models.IntegerField(default=0)
    total_protein = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    total_carbs = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    total_fats = models.DecimalField(max_digits=6, decimal_places=1, default=0)
    total_fiber = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    
    # Water intake
    water_intake = models.DecimalField(max_digits=4, decimal_places=1, default=0, help_text="Water intake in liters")
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']
        verbose_name = "Nutrition Log"
        verbose_name_plural = "Nutrition Logs"


class MealLog(models.Model):
    """Individual meals logged by users"""
    
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('morning_snack', 'Morning Snack'),
        ('lunch', 'Lunch'),
        ('afternoon_snack', 'Afternoon Snack'),
        ('dinner', 'Dinner'),
        ('evening_snack', 'Evening Snack'),
    ]
    
    nutrition_log = models.ForeignKey(NutritionLog, on_delete=models.CASCADE, related_name='meals')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='meal_logs', null=True, blank=True)
    
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    meal_name = models.CharField(max_length=200, help_text="Name of the meal")
    
    # Nutrition (can be from recipe or manually entered)
    calories = models.IntegerField()
    protein = models.DecimalField(max_digits=6, decimal_places=1)
    carbs = models.DecimalField(max_digits=6, decimal_places=1)
    fats = models.DecimalField(max_digits=6, decimal_places=1)
    
    servings = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    
    # Time
    time = models.TimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to='meal_logs/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nutrition_log.user.username} - {self.meal_type}: {self.meal_name}"
    
    class Meta:
        ordering = ['nutrition_log', 'meal_type']
        verbose_name = "Meal Log"
        verbose_name_plural = "Meal Logs"


class FoodItem(models.Model):
    """Database of individual food items for quick logging"""
    
    CATEGORY_CHOICES = [
        ('fruit', 'Fruit'),
        ('vegetable', 'Vegetable'),
        ('protein', 'Protein'),
        ('grain', 'Grain'),
        ('dairy', 'Dairy'),
        ('snack', 'Snack'),
        ('beverage', 'Beverage'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    brand = models.CharField(max_length=100, blank=True)
    
    # Nutrition per serving
    serving_size = models.CharField(max_length=100, help_text="e.g., 1 cup, 100g")
    calories = models.IntegerField()
    protein = models.DecimalField(max_digits=6, decimal_places=1)
    carbs = models.DecimalField(max_digits=6, decimal_places=1)
    fats = models.DecimalField(max_digits=6, decimal_places=1)
    fiber = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    # Tags
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.serving_size})"
    
    class Meta:
        ordering = ['name']
        verbose_name = "Food Item"
        verbose_name_plural = "Food Items"