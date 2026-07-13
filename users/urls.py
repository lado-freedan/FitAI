from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, GenerateAIPlanView, UpdateUserProfileView, DailyLogView, WeeklyAnalysisView, AIPlanHistoryView, BodyVisionAnalysisView, UserMeProfileView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("generate-plan/", GenerateAIPlanView.as_view(), name="generate_ai_plan"),
    path("profile/update/", UpdateUserProfileView.as_view(), name="update_user_profile"),
    path("daily-log/", DailyLogView.as_view(), name="daily_log"),
    path("weekly-analysis/", WeeklyAnalysisView.as_view(), name="weekly_analysis"),
    path("plans/history/", AIPlanHistoryView.as_view(), name="plan_history"),
    path("body-analysis/upload/", BodyVisionAnalysisView.as_view(), name="body_analysis_upload"),
    path("me/", UserMeProfileView.as_view(), name="user_me_profile"),
]