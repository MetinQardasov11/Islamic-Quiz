from django.shortcuts import render


def login(request):
    return render(request, 'auth/login.html')


def register(request):
    return render(request, 'auth/register.html')


def profile(request):
    return render(request, 'auth/profile.html')


def forgot_password(request):
    return render(request, 'auth/forgot-password.html')


def otp(request):
    return render(request, 'auth/otp.html')


def set_new_password(request):
    return render(request, 'auth/set-new-password.html')
