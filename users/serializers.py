from rest_framework import serializers
from django.contrib.auth.models import User

from .models import UserProfile, DailyLog, AIPlan, BodyAnalysisRequest


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "gender", "fitness_category", "fitness_goal",
            "age", "weight", "height", "phone_number", "country",
            "is_vegetarian", "requires_halal",
            "workout_location", "workout_days_per_week"
        ]

class RegisterSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ["username", "password", "email", "first_name", "last_name", "profile"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Entered email already exists.")
        return value

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )

        UserProfile.objects.create(user=user, **profile_data)

        return user
    

class DailyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyLog
        fields = ["id", "date", "water_intake_ml", "calories_consumed", "workout_completed", "notes"]
        read_only_fields = ["id", "date"]


class AIPlanHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPlan
        fields = ["id", "plan_type", "content", "created_at", "is_active"]


class BodyAnalysisUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyAnalysisRequest
        fields = ["id", "image_front", "image_back", "image_side_left", "image_side_right", "uploaded_at", "ai_analysis_result", "is_processed"]
        read_only_fields = ["id", "uploaded_at", "ai_analysis_result", "is_processed"]


class FullUserProfileSerializer(serializers.ModelSerializer):
    profile_details = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "profile_details"]

    def get_profile_details(self, obj):
        profile = getattr(obj, "profile", None)
        if profile:
            return {
                "weight": profile.weight,
                "fitness_goal": profile.fitness_goal,
                "workout_location": profile.workout_location,
                "workout_days_per_week": profile.workout_days_per_week,
            }
        return None