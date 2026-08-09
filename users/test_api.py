from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


User = get_user_model()

class FitAIBaseAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("token_obtain_pair")
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "profile": {
                "gender": "MALE",
                "fitness_category": "BOXING",
                "fitness_goal": "MUSCLE_GAIN",
                "age": 25,
                "weight": 75.0,
                "height": 175.0,
                "phone_number": "+995500000000",
                "country": "Georgia",
                "is_vegetarian": False,
                "reguires_halal": False,
                "workout_location": "GYM",
                "workout_days_per_week": 4
            }
        }
        self.user = User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"]
        )

    def test_user_registration(self):
        new_user_payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "AnotherPassword123!",
            "first_name": "New",
            "last_name": "User",
            "profile": {
                "gender": "MALE",
                "fitness_category": "FITNESS",
                "fitness_goal": "WEIGHT_LOSS",
                "age": 28,
                "weight": 80.0,
                "height": 180.0,
                "phone_number": "+995511111111",
                "country": "Georgia",
                "is_vegetarian": False,
                "requires_halal": False,
                "workout_location": "HOME_BAND",
                "workout_days_per_week": 3
            }
        }
        response = self.client.post(self.register_url, new_user_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login_and_jwt_token(self):
        login_payload = {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        }
        response = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_authenticated_endpoint_access(self):
        self.client.force_authenticate(user=self.user)
        me_url = reverse("user_me_profile")
        responde = self.client.get(me_url)
        self.assertEqual(responde.status_code, status.HTTP_200_OK)