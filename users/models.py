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

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    fitness_category = models.CharField(max_length=20, choices=FITNESS_CATEGORIES)
    fitness_goal = models.CharField(max_length=20, choices=FITNESS_GOALS)

    age = models.PositiveIntegerField(validators=[MinValueValidator(10), MaxValueValidator(100)])
    weight = models.FloatField(validators=[MinValueValidator(30.0), MaxValueValidator(250.0)], help_text="weight in kg")
    height = models.FloatField(validators=[MinValueValidator(100.0), MaxValueValidator(250.0)], help_text="height in cm")

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
    