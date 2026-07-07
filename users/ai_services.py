import os
from google import genai

from django.conf import settings


class GeminaiFitnessService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

    def generate_workout_and_diet_plan(self, user_profile):
        diet_info = []
        if user_profile.is_vegetarian:
            diet_info.append("Vegetarian (No meat/No fish)")
        if user_profile.requires_halal:
            diet_info.append("Strictly Halal food only")

        diet_constraints = ", ".join(diet_info) if diet_info else "No Specific restrictions"
        workout_env = user_profile.get_workout_location_display()

        prompt = f"""
        You are an expert AI Personal Trainer and Nutritionist.
        Generate a comprehensive, highly personalized 7-day fitness and nutrition plan based on the following user profile:
        - Gender: {user_profile.gender}
        - Age: {user_profile.age} years old
        - Weight: {user_profile.weight} kg
        - Height: {user_profile.height} cm
        - Fitness Category: {user_profile.fitness_category}
        - Fitness Goal: {user_profile.fitness_goal}
        - Workout Enviroment/Equipment: {workout_env}
        - Country/Location: {user_profile.country}
        - Dietary Restrictions: {diet_constraints}

        Requirements for the output:
        1. Provide a daily workout routine SRTICTLY tailord to their workout enviroment and equipment (e.g., if bodyweight only, do not include gym machins or dumbells; focus on push-ups, pull-ups, dips and calisthenics).
        2. Provide a daily meal plan (Breakfast, Lunch, Dinner, Snacks) that strictly respects their dietary restrictions (e.g., if vegetarian, do not include chicken or beef or animal products; if halal, respect halal guidlines)
        3. Keep the tone morivational and professional.
        4. Return the response formatted clearly in clean markdown.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"Error communicationg with Gemini API: {str(e)}"