import os
import PIL.Image
from google import genai

from django.conf import settings


class GeminaiFitnessService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-3.5-flash"

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
        

    def generate_weekly_progress_analysis(self, user_profile, logs_data):
        logs_summary = ""
        for log in logs_data:
            status = "Completed" if log.workout_completed else "Missed"
            logs_summary += f'- Date: {log.date} | Water: {log.water_intake_ml}ml | Calories: {log.calories_consumed} kcal | Workout: {status} | Notes: {log.notes or "None"}\n'

        prompt = f"""
        You are an expert AI Fitness Coach and Behavioral Analyst.
        Analyze the user's daily tracking logs from the past week and provide a constractive, motivating and analytical feedback report.
        
        User Profile:
        - Goal: {user_profile.fitness_goal}
        - Current Weight: {user_profile.weight} kg

        Weekly Logs Data:
        {logs_summary}

        Requirements for output:
        1. Evaluate their consistency (Workout completion rate, Hydration levels and Calories intake relative to their goal).
        2. Identify positive patterns or areas that need immediate improvment.
        3. Provide 2-3 highly actionable tips for upcoming week.
        4. Keep the tone inspiring, direct and professional.
        5. Return the response formatted clearly in clean Markdown (in english language).
        """

        try:
            from google import genai
            client = genai.Client()
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"Error communicationg with Gemini API: {str(e)}"
        

    def analyze_body_images_and_generate_plan(self, user_profile, front_path, back_path, left_path, right_path):
        try:
            img_front = PIL.Image.open(front_path)
            img_back = PIL.Image.open(back_path)
            img_left = PIL.Image.open(left_path)
            img_right = PIL.Image.open(right_path)

            prompt = f"""
            You are a strict AI Medical Fitness Coach and Visual Posture Expert .
            You are examing 4 images provided in this exact order:
            1. Front view, 2. Baack view, 3. Left Side view, 4. Right side view.

            User Profile Context:
            - Goal: {user_profile.fitness_goal}
            - Current Weight: {user_profile.weight} kg
            - Desired Workout Frequency: {user_profile.workout_days_per_week} days per week. IMPORTANT: The Schedule must span exactly this many days.

            CRITICAL STEP-BY-STEP AUDIT:
            Step 1: Inspext the clothing on ALL images. The user MUST be wearing tight gym clothes, shorts or sports tops. If they are wearing baggy jeans, winter jackets or loose clothes that completely hide the body contours or if they are completely nude, REJECT immediately.
            Step 2: Verify the aangels. The "Left Side" must show the the left profile, the "Back" must show the spine/shoulder blades. If the user mixed up the files, you must catch it.

            If Step 1 or Step 2 fails, stop everything and return ONLY this message:
            "Error: Sent photos are against sport ruls of aapplication or they are not in correct angels"

            If validation passes, proceed to analyze posture and build a highly tailored weekly program split across exactly {user_profile.workout_days_per_week} workout days based on their goal.
            """

            client = genai.Client()
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=[prompt, img_front, img_back, img_left, img_right]
            )
            return response.text
        except Exception as e:
            return f"Error communicating with Gemini Vision API: {str(e)}"