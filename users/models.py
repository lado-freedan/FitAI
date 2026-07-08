from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    FITNESS_CATEGORIES = [
        ("BODYBUILDING", "BodyBuilding"),
        ("POWERLIFTING", "PowerLifting"),
        ("BOXING", "Boxing"),
        ("WRESTLING", "Wrestling"),
        ("CROSSFIT", "Crossfit"),
        ("FITNESS", "Fitness"),
    ]

    FITNESS_GOALS = [
        ("WEIGHT_LOSS", "WeightLoss"),
        ("MUSCLE_GAIN", "MuscleGain"),
        ("STRENGTH", "Strength"),
        ("ENDURANCE", "Endurance")
    ]


    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
    ]

    class WorkoutLocation(models.TextChoices):
        GYM = "GYM", "Gym (Full Equipment)"
        HOME_BAND = "HOME_BAND", "Home with Resistance Bands"
        BODYWEIGHT = "BODYWEIGHT", "Bodyweight Only (Calisthenics, Pull-ups, Push-ups)"

    workout_location = models.CharField(
        max_length=20,
        choices=WorkoutLocation.choices,
        default=WorkoutLocation.GYM,
        help_text="Where and with what equipment the user works out"
    )

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    fitness_category = models.CharField(max_length=20, choices=FITNESS_CATEGORIES)
    fitness_goal = models.CharField(max_length=20, choices=FITNESS_GOALS)

    age = models.PositiveIntegerField(validators=[MinValueValidator(10), MaxValueValidator(100)])
    weight = models.FloatField(validators=[MinValueValidator(30.0), MaxValueValidator(250.0)], help_text="weight in kg")
    height = models.FloatField(validators=[MinValueValidator(100.0), MaxValueValidator(250.0)], help_text="height in cm")

    is_vegetarian = models.BooleanField(default=False)
    requires_halal = models.BooleanField(default=False)

    phone_regex = RegexValidator(
        regex=r'^\+\d{9,15}$',
        message="phone number must be in this format: +995*********"
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, help_text="phone number")

    country_regex = RegexValidator(
        regex=r'^[a-zA-Z\s]+$',
        message="country name must be by alphabets"
    )
    country = models.CharField(validators=[country_regex], max_length=50, default="Georgia", help_text="country name")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"profile for {self.user.username} - {self.get_fitness_category_display()}"
    

class AIPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fitness_plans")
    plan_type = models.CharField(max_length=50, default="COMBINED")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Plan for {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"
    

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_logs")
    date = models.DateField(auto_now_add=True)

    water_intake_ml = models.IntegerField(default=0, help_text="Water intake in milliliters")
    calories_consumed = models.IntegerField(default=0, help_text="Calories consumed today")
    workout_completed = models.BooleanField(default=False, help_text="Did the user complete today's workout?")
    notes = models.TextField(blank=True, null=True, help_text="Any optional notes from the user")

    class Meta:
        ordering = ["-date"]
        unique_together = ("user", "date")

    def __str__(self):
        return f"Log for {self.user.username} on {self.date}"