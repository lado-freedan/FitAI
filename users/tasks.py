from celery import shared_task

from .models import BodyAnalysisRequest, AIPlan
from .ai_services import GeminiFitnessService


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def analyze_body_photo_task(self, analysis_id, profile_id):
    from .models import UserProfile

    analysis = BodyAnalysisRequest.objects.get(id=analysis_id)
    profile = UserProfile.objects.get(id=profile_id)

    try:
        ai_service = GeminiFitnessService()

        analysis_result = ai_service.analyze_body_images_and_generate_plan(
            user_profile=profile,
            front_path=analysis.image_front,
            back_path=analysis.image_back,
            left_path=analysis.image_side_left,
            right_path=analysis.image_side_right
        )

        AIPlan.objects.filter(user=profile.user, is_active=True).update(is_active=False)

        AIPlan.objects.create(
            user=profile.user,
            plan_type="COMBINED",
            content=analysis_result,
            is_active=True,
            has_visual_analysis=True
        )

        analysis.ai_analysis_result = analysis_result
        analysis.is_processed = True
        analysis.status = "completed"
        analysis.save()

    except Exception as e:
        if self.request.retries == self.max_retries:
            analysis.status = "failed"
            analysis.save()
        raise e