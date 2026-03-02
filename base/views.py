import json

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import MultiplayerSession


def index(request):
    return render(request, 'base/index.html')


def faq(request):
    return render(request, 'base/faq.html')


def terms_of_use(request):
    return render(request, 'base/terms-of-use.html')


def quizzes(request):
    return render(request, 'quiz/quizzes.html')


def quiz(request):
    return render(request, 'quiz/quiz.html')


def result(request):
    return render(request, 'quiz/result.html')


def review(request):
    return render(request, 'quiz/review.html')


def multiplayer(request):
    return render(request, 'quiz/multiplayer.html')


def page_not_found(request):
    return render(request, 'base/404.html', status=404)


# ---------------------------------------------------------------------------
# API: Çok Oyunculu Maç Kaydet
# ---------------------------------------------------------------------------

@login_required
@require_POST
def save_multiplayer_session(request):
    try:
        data = json.loads(request.body)

        quiz_id          = str(data.get('quiz_id', '')).strip()
        quiz_title       = str(data.get('quiz_title', '')).strip()
        player_one_name  = str(data.get('player_one_name', '')).strip()
        player_two_name  = str(data.get('player_two_name', '')).strip()
        player_one_score = int(data.get('player_one_score', 0))
        player_two_score = int(data.get('player_two_score', 0))
        total_questions  = int(data.get('total_questions', 0))
        winner           = str(data.get('winner', '')).strip()
        status           = data.get('status', MultiplayerSession.STATUS_COMPLETED)

        if status not in (MultiplayerSession.STATUS_COMPLETED, MultiplayerSession.STATUS_TIME_UP):
            status = MultiplayerSession.STATUS_COMPLETED

        if not quiz_id or not player_one_name or not player_two_name:
            return JsonResponse({'success': False, 'error': 'Eksik alan.'}, status=400)

        session = MultiplayerSession.objects.create(
            host=request.user,
            quiz_id=quiz_id,
            quiz_title=quiz_title,
            player_one_name=player_one_name,
            player_two_name=player_two_name,
            player_one_score=player_one_score,
            player_two_score=player_two_score,
            total_questions=total_questions,
            winner=winner,
            status=status,
        )

        return JsonResponse({'success': True, 'session_id': session.id})

    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=400)
