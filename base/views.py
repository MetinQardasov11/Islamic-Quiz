from django.shortcuts import render


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
