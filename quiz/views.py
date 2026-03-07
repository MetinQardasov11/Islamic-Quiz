import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from authentication.models import UserProfile

from .models import (
    MultiplayerSession,
    Quiz,
    QuizAnswerOption,
    QuizAttempt,
    QuizAttemptAnswer,
    QuizQuestion,
)


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


def serialize_question(question, index):
    answer_options = list(getattr(question, 'active_answer_options', []))
    if answer_options:
        options = [
            {
                'text': option.text,
                'image': option.image_url,
                'imageAlt': option.image_alt,
            }
            for option in answer_options
        ]
        correct_answer = next(
            (option_index for option_index, option in enumerate(answer_options) if option.is_correct),
            0,
        )
    else:
        options = [
            {
                'text': option,
                'image': '',
                'imageAlt': '',
            }
            for option in (question.options if isinstance(question.options, list) else [])
        ]
        correct_answer = question.correct_answer

    return {
        'id': question.pk or index + 1,
        'questionType': question.question_type,
        'question': question.question,
        'options': options,
        'correctAnswer': correct_answer,
        'image': question.image_url,
        'imageAlt': question.image_alt,
        'imageCaption': question.image_caption,
    }


def serialize_quiz(quiz_instance):
    questions = [
        serialize_question(question, index)
        for index, question in enumerate(getattr(quiz_instance, 'active_questions', []))
    ]
    return {
        'id': quiz_instance.slug,
        'title': quiz_instance.title,
        'description': quiz_instance.description,
        'difficulty': quiz_instance.difficulty,
        'category': quiz_instance.category.name,
        'thumbnail': quiz_instance.thumbnail_url,
        'timeLimit': quiz_instance.time_limit,
        'questions': questions,
        'subcategory': quiz_instance.subcategory,
    }


def serialize_attempt(attempt):
    return {
        'id': attempt.id,
        'quizId': attempt.quiz.slug,
        'quizTitle': attempt.quiz.title,
        'correctCount': attempt.correct_count,
        'totalQuestions': attempt.total_questions,
        'percentage': attempt.percentage,
        'passed': attempt.passed,
        'elapsedSeconds': attempt.elapsed_seconds,
        'createdAt': attempt.created_at.isoformat(),
        'answers': [
            {
                'questionOrder': answer.question_order,
                'questionText': answer.question_text,
                'selectedAnswerIndex': answer.selected_answer_index,
                'selectedAnswerText': answer.selected_answer_text,
                'selectedAnswerImage': answer.selected_answer_image,
                'selectedAnswerImageAlt': answer.selected_answer_image_alt,
                'correctAnswerIndex': answer.correct_answer_index,
                'correctAnswerText': answer.correct_answer_text,
                'correctAnswerImage': answer.correct_answer_image,
                'correctAnswerImageAlt': answer.correct_answer_image_alt,
                'isCorrect': answer.is_correct,
                'image': answer.image,
                'imageAlt': answer.image_alt,
                'imageCaption': answer.image_caption,
            }
            for answer in attempt.answers.all().order_by('question_order', 'id')
        ],
    }


def update_user_profile_stats(user):
    profile = getattr(user, 'profile', None)
    if profile is None:
        return

    attempts = user.quiz_attempts.select_related('quiz').all()
    total_quizzes = attempts.count()
    total_score = sum(attempt.percentage for attempt in attempts)
    total_correct = sum(attempt.correct_count for attempt in attempts)
    total_questions = sum(attempt.total_questions for attempt in attempts)

    profile.total_quizzes_completed = total_quizzes
    profile.total_score = total_score
    profile.total_correct_answers = total_correct
    profile.total_questions_answered = total_questions
    profile.update_streak()

    xp_points = total_score + (total_quizzes * 10)
    profile.xp_points = xp_points
    profile._recalculate_level()
    profile.save(
        update_fields=[
            'total_quizzes_completed',
            'total_score',
            'total_correct_answers',
            'total_questions_answered',
            'current_streak',
            'longest_streak',
            'last_activity_date',
            'xp_points',
            'level',
        ]
    )


def quizzes_api(request):
    answer_option_prefetch = Prefetch(
        'answer_options',
        queryset=QuizAnswerOption.objects.filter(is_active=True).order_by('display_order', 'id'),
        to_attr='active_answer_options',
    )
    quizzes_queryset = (
        Quiz.objects.filter(is_active=True, category__is_active=True)
        .select_related('category')
        .prefetch_related(
            Prefetch(
                'questions',
                queryset=QuizQuestion.objects.filter(is_active=True)
                .prefetch_related(answer_option_prefetch)
                .order_by('display_order', 'id'),
                to_attr='active_questions',
            )
        )
        .order_by('display_order', 'title')
    )
    serialized_quizzes = [serialize_quiz(quiz_instance) for quiz_instance in quizzes_queryset]
    passing_score = 70
    if quizzes_queryset:
        passing_score = quizzes_queryset[0].passing_score

    return JsonResponse({
        'quizzes': serialized_quizzes,
        'passingScore': passing_score,
    })


@login_required
@require_POST
def submit_quiz_attempt(request):
    try:
        payload = json.loads(request.body)
        quiz_id = str(payload.get('quiz_id', '')).strip()
        raw_answers = payload.get('answers', [])
        elapsed_seconds = int(payload.get('elapsed_seconds', 0))
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=400)

    if not quiz_id or not isinstance(raw_answers, list):
        return JsonResponse({'success': False, 'error': 'Geçersiz quiz verisi.'}, status=400)

    quiz_instance = get_object_or_404(
        Quiz.objects.prefetch_related(
            Prefetch(
                'questions',
                queryset=QuizQuestion.objects.filter(is_active=True)
                .prefetch_related(
                    Prefetch(
                        'answer_options',
                        queryset=QuizAnswerOption.objects.filter(is_active=True).order_by('display_order', 'id'),
                        to_attr='active_answer_options',
                    )
                )
                .order_by('display_order', 'id'),
                to_attr='active_questions',
            )
        ),
        slug=quiz_id,
        is_active=True,
        category__is_active=True,
    )

    questions = list(getattr(quiz_instance, 'active_questions', []))
    if not questions:
        return JsonResponse({'success': False, 'error': 'Bu quizde soru yok.'}, status=400)

    answers = raw_answers[:len(questions)]
    if len(answers) < len(questions):
        answers.extend([None] * (len(questions) - len(answers)))

    with transaction.atomic():
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz_instance,
            total_questions=len(questions),
            elapsed_seconds=max(elapsed_seconds, 0),
        )

        correct_count = 0
        attempt_answers = []

        for index, question in enumerate(questions):
            answer_options = list(getattr(question, 'active_answer_options', []))
            if answer_options:
                option_payload = answer_options
                correct_index = next(
                    (option_index for option_index, option in enumerate(answer_options) if option.is_correct),
                    0,
                )
            else:
                option_payload = [
                    QuizAnswerOption(
                        text=option,
                        image='',
                        image_alt='',
                        is_correct=(option_index == question.correct_answer),
                    )
                    for option_index, option in enumerate(
                        question.options if isinstance(question.options, list) else []
                    )
                ]
                correct_index = question.correct_answer

            selected_index = answers[index]
            if selected_index in ('', 'null'):
                selected_index = None
            if selected_index is not None:
                try:
                    selected_index = int(selected_index)
                except (TypeError, ValueError):
                    selected_index = None

            is_valid_selected_index = (
                selected_index is not None and 0 <= selected_index < len(option_payload)
            )
            selected_option = option_payload[selected_index] if is_valid_selected_index else None
            correct_option = option_payload[correct_index] if 0 <= correct_index < len(option_payload) else None
            selected_text = selected_option.text if selected_option else ''
            selected_image = selected_option.image_url if selected_option else ''
            selected_image_alt = selected_option.image_alt if selected_option else ''
            correct_text = correct_option.text if correct_option else ''
            correct_image = correct_option.image_url if correct_option else ''
            correct_image_alt = correct_option.image_alt if correct_option else ''
            is_correct = selected_index == correct_index
            if is_correct:
                correct_count += 1

            attempt_answers.append(
                QuizAttemptAnswer(
                    attempt=attempt,
                    question_order=index,
                    question_text=question.question,
                    selected_answer_index=selected_index,
                    selected_answer_text=selected_text,
                    selected_answer_image=selected_image,
                    selected_answer_image_alt=selected_image_alt,
                    correct_answer_index=correct_index,
                    correct_answer_text=correct_text,
                    correct_answer_image=correct_image,
                    correct_answer_image_alt=correct_image_alt,
                    is_correct=is_correct,
                    image=question.image_url,
                    image_alt=question.image_alt,
                    image_caption=question.image_caption,
                )
            )

        QuizAttemptAnswer.objects.bulk_create(attempt_answers)

        percentage = round((correct_count / len(questions)) * 100)
        attempt.correct_count = correct_count
        attempt.percentage = percentage
        attempt.passed = percentage >= quiz_instance.passing_score
        attempt.save(update_fields=['correct_count', 'percentage', 'passed'])

        update_user_profile_stats(request.user)

    return JsonResponse({
        'success': True,
        'attempt': serialize_attempt(
            QuizAttempt.objects.select_related('quiz').prefetch_related('answers').get(pk=attempt.pk)
        ),
    })


@login_required
def quiz_attempt_detail(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz', 'quiz__category').prefetch_related('answers'),
        pk=attempt_id,
        user=request.user,
    )
    return JsonResponse({'success': True, 'attempt': serialize_attempt(attempt)})


@login_required
@require_POST
def save_multiplayer_session(request):
    try:
        data = json.loads(request.body)

        quiz_id = str(data.get('quiz_id', '')).strip()
        quiz_title = str(data.get('quiz_title', '')).strip()
        player_one_name = str(data.get('player_one_name', '')).strip()
        player_two_name = str(data.get('player_two_name', '')).strip()
        player_one_score = int(data.get('player_one_score', 0))
        player_two_score = int(data.get('player_two_score', 0))
        total_questions = int(data.get('total_questions', 0))
        winner = str(data.get('winner', '')).strip()
        status = data.get('status', MultiplayerSession.STATUS_COMPLETED)

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
