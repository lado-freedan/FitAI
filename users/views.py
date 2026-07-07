from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth.models import User

from .serializers import RegisterSerializer
from .ai_services import GeminaiFitnessService
from .models import AIPlan


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "User registered successfully.",
            "token":{ 
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    

class GenerateAIPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not hasattr(user, "profile"):
            return Response(
                {"error": "Please first create your profile"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        profile = user.profile

        active_plan = AIPlan.objects.filter(user=user, is_active=True).first()
        if active_plan:
            return Response({
                "username": user.username,
                "goal": profile.fitness_goal,
                "source": "database.cache",
                "ai_generated_plan": active_plan.content
            }, status=status.HTTP_200_OK)

        ai_service = GeminaiFitnessService()
        plan_text = ai_service.generate_workout_and_diet_plan(profile)

        if plan_text.startswith("Error"):
            return Response({
                "Error": "AI generation system is busy at the moment, Please try again later",
                "details": plan_text
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        AIPlan.objects.create(
            user=user,
            content=plan_text,
            is_active=True
        )

        return Response({
            "username": user.username,
            "goal": profile.fitness_goal,
            "source": "gemini_api",
            "ai_generated_plan": plan_text
        }, status=status.HTTP_200_OK)