from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from datetime import date, timedelta

from .serializers import RegisterSerializer, UserProfileSerializer, DailyLogSerializer, AIPlanHistorySerializer, BodyAnalysisUploadSerializer, FullUserProfileSerializer
from .ai_services import GeminaiFitnessService
from .models import AIPlan, UserProfile, DailyLog, BodyAnalysisRequest


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
    

class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            AIPlan.objects.filter(user=user, is_active=True).update(is_active=False)

            return Response({
                "message": "Your profile is updated and old plan is expired",
                "profile": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DailyLogView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        today = date.today()

        log_instance, create = DailyLog.objects.get_or_create(user=user, date=today)
        serializer = DailyLogSerializer(log_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            message = "Daily log accepted" if create else "Daily log updated"
            return Response({
                "message": message,
                "log": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        user=request.user
        today = date.today()
        log_instance = DailyLog.objects.filter(user=user, date=today).first()

        if not log_instance:
            return Response({"message": "Not any log entered", "log": None}, status=status.HTTP_200_OK)
        
        serializer = DailyLogSerializer(log_instance)
        return Response({"log": serializer.data}, status=status.HTTP_200_OK)
    

class WeeklyAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, "profile", None)

        if not profile:
            return Response({"error": "Profile not founded"}, status=status.HTTP_400_BAD_REQUEST)
        
        today = date.today()
        on_week_ago = today - timedelta(days=7)

        logs = DailyLog.objects.filter(user=user, date__range=[on_week_ago, today]).order_by("date")
        if not logs.exists():
            return Response({
                "message": "For taking weekly report , you must been at least 1week in program"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ai_service = GeminaiFitnessService()
        analysis_report = ai_service.generate_weekly_progress_analysis(profile, logs)

        return Response({
            "username": user.username,
            "period": f"{on_week_ago} to {today}",
            "logs_analyzed_count": logs.count(),
            "progress_analysis": analysis_report
        }, status=status.HTTP_200_OK)
    

class AIPlanHistoryView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AIPlanHistorySerializer

    def get_queryset(self):
        return AIPlan.objects.filter(user=self.request.user).order_by("-created_at")
    

class BodyVisionAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        user = request.user
        profile = getattr(user, "profile", None)

        if not profile:
            return Response({"error": "First create your profile"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.FILES:
            cached_plan = AIPlan.objects.filter(user=user, is_active=True, has_visual_analysis=True).first()
            if cached_plan:
                return Response({
                    "message": "Taking visual plan from chache data",
                    "source": "database_cache",
                    "analysis_and_plan": cached_plan.content
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "There is no photo sent and there is not any active plan"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = BodyAnalysisUploadSerializer(data=request.data)

        if serializer.is_valid():
            analysis_instance = serializer.save(user=user)
            front_path = analysis_instance.image_front.path
            back_path = analysis_instance.image_back.path
            left_path = analysis_instance.image_side_left.path
            right_path = analysis_instance.image_side_right.path

            ai_service = GeminaiFitnessService()
            analysis_result = ai_service.analyze_body_images_and_generate_plan(
                profile, front_path, back_path, left_path, right_path
            )

            AIPlan.objects.filter(user=user, is_active=True).update(is_active=False)
            AIPlan.objects.create(
                user=user,
                plan_type="COMBINED",
                content=analysis_result,
                is_active=True,
                has_visual_analysis=True
            )

            analysis_instance.ai_analysis_result = analysis_result
            analysis_instance.is_processed = True
            analysis_instance.save()

            return Response({
                "message": "Photos analized seccessfully",
                "source": "gemini_vision_api",
                "analysis_and_plan": analysis_result
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserMeProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = FullUserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)