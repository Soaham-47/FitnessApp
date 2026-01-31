from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile for fitness tracking"""
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('light', 'Lightly active (1-3 days/week)'),
        ('moderate', 'Moderately active (3-5 days/week)'),
        ('very', 'Very active (6-7 days/week)'),
        ('extra', 'Extra active (athlete/physical job)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Info
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height in cm", null=True, blank=True)
    
    # Fitness Info
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kg", null=True, blank=True)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, default='moderate')
    
    # Profile
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile whenever the user is saved"""
    instance.profile.save()


class Goal(models.Model):
    """User fitness goals"""
    
    GOAL_TYPE_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Build Endurance'),
        ('strength', 'Build Strength'),
        ('flexibility', 'Improve Flexibility'),
        ('general', 'General Fitness'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Target metrics
    target_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Target weight in kg")
    target_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    progress_percentage = models.IntegerField(default=0, help_text="Progress from 0-100%")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Goal"
        verbose_name_plural = "Goals"


class ProgressLog(models.Model):
    """Track user progress over time"""
    
    METRIC_TYPE_CHOICES = [
        ('weight', 'Weight'),
        ('body_fat', 'Body Fat %'),
        ('muscle_mass', 'Muscle Mass'),
        ('waist', 'Waist Circumference'),
        ('chest', 'Chest Circumference'),
        ('arms', 'Arm Circumference'),
        ('legs', 'Leg Circumference'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_logs')
    date = models.DateField()
    
    # Measurements
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    body_fat_percentage = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    muscle_mass = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Muscle mass in kg")
    
    # Circumferences in cm
    waist = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    chest = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    arms = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    legs = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    photo = models.ImageField(upload_to='progress_photos/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Progress Log"
        verbose_name_plural = "Progress Logs"
        unique_together = ['user', 'date']


class Achievement(models.Model):
    """User achievements and milestones"""
    
    ACHIEVEMENT_TYPE_CHOICES = [
        ('workout', 'Workout Milestone'),
        ('streak', 'Streak Achievement'),
        ('weight', 'Weight Goal'),
        ('strength', 'Strength Milestone'),
        ('endurance', 'Endurance Milestone'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='🏆', help_text="Emoji or icon")
    
    earned_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    class Meta:
        ordering = ['-earned_at']
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"