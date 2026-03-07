from quiz.models import Quiz, QuizAttempt, QuizCategory, QuizQuestion

from .models import SiteSettings, SocialLink


def site_content(request):
    site_settings = SiteSettings.objects.order_by('id').first()
    social_links = SocialLink.objects.filter(is_active=True).order_by('display_order', 'label')
    active_quizzes = Quiz.objects.filter(is_active=True, category__is_active=True)
    attempts = QuizAttempt.objects.all()
    attempt_count = attempts.count()
    average_score = round(sum(attempt.percentage for attempt in attempts) / attempt_count) if attempt_count else 0
    return {
        'site_settings': site_settings,
        'site_social_links': social_links,
        'site_metrics': {
            'quiz_count': active_quizzes.count(),
            'category_count': QuizCategory.objects.filter(is_active=True).count(),
            'question_count': QuizQuestion.objects.filter(is_active=True, quiz__is_active=True).count(),
            'attempt_count': attempt_count,
            'average_score': average_score,
        },
    }
