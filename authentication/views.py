import json

from django.shortcuts import render, redirect
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
    update_session_auth_hash,
)
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from content.models import SiteSettings
from quiz.models import QuizAttempt

from .models import User, OTPCode
from .forms import (
    RegisterForm,
    LoginForm,
    ForgotPasswordForm,
    OTPForm,
    SetNewPasswordForm,
)


# ---------------------------------------------------------------------------
# Yardımcı: OTP e-postası gönder
# ---------------------------------------------------------------------------

def _send_otp_email(user: User, otp: OTPCode) -> None:
    site_name = SiteSettings.objects.order_by('id').values_list('site_name', flat=True).first() or 'Quiz'
    subject = f'{site_name} — Şifre Sıfırlama Kodunuz'
    body = (
        f'Merhaba {user.first_name or user.username},\n\n'
        f'Şifre sıfırlama talebiniz için doğrulama kodunuz:\n\n'
        f'    {otp.code}\n\n'
        f'Bu kod {OTPCode.EXPIRY_MINUTES} dakika boyunca geçerlidir.\n'
        f'Eğer bu isteği siz yapmadıysanız bu e-postayı dikkate almayınız.\n\n'
        f'— {site_name} Ekibi'
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

def register(request):
    if request.user.is_authenticated:
        return redirect('quiz:quizzes')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        name  = form.cleaned_data['name']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name  = name_parts[1] if len(name_parts) > 1 else ''

        base_username = email.split('@')[0]
        username, counter = base_username, 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1

        User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        messages.success(request, f'Hesabın oluşturuldu, {first_name}! Şimdi giriş yapabilirsin.')
        return redirect('authentication:login')

    return render(request, 'auth/register.html', {'form': form})


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def login(request):
    if request.user.is_authenticated:
        auth_logout(request)

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email       = form.cleaned_data['email'].lower()
        password    = form.cleaned_data['password']
        remember_me = form.cleaned_data['remember_me']

        user = authenticate(request, email=email, password=password)

        if user is not None:
            auth_login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            next_url = request.GET.get('next') or 'quiz:quizzes'
            messages.success(request, f'Hoş geldin, {user.first_name or user.email}!')
            return redirect(next_url)

        messages.error(request, 'E-posta veya şifre hatalı.')

    return render(request, 'auth/login.html', {'form': form})


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

def logout(request):
    auth_logout(request)
    messages.success(request, 'Çıkış yapıldı.')
    return redirect('authentication:login')


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

def profile(request):
    if not request.user.is_authenticated:
        return redirect('authentication:login')

    profile_obj = request.user.profile
    attempts = list(
        QuizAttempt.objects.filter(user=request.user)
        .select_related('quiz', 'quiz__category')
        .order_by('-created_at')
    )

    total_quizzes = profile_obj.total_quizzes_completed
    avg_score = round((profile_obj.total_score / total_quizzes), 1) if total_quizzes else 0
    best_score = max((attempt.percentage for attempt in attempts), default=0)
    passed_count = sum(1 for attempt in attempts if attempt.passed)
    failed_count = total_quizzes - passed_count
    total_time_seconds = sum(attempt.elapsed_seconds for attempt in attempts)
    total_time_minutes, remaining_seconds = divmod(total_time_seconds, 60)
    if total_time_minutes and remaining_seconds:
        total_time_display = f'{total_time_minutes} dk {remaining_seconds} sn'
    elif total_time_minutes:
        total_time_display = f'{total_time_minutes} dk'
    else:
        total_time_display = f'{remaining_seconds} sn'
    category_stats = {}
    for attempt in attempts:
        category_name = attempt.quiz.category.name
        category_stats.setdefault(category_name, []).append(attempt.percentage)

    category_performance = [
        {
            'name': category_name,
            'average': round(sum(scores) / len(scores)),
        }
        for category_name, scores in category_stats.items()
    ]

    context = {
        'profile_user': request.user,
        'profile_obj': profile_obj,
        'recent_attempts': attempts[:4],
        'total_quizzes': total_quizzes,
        'avg_score': avg_score,
        'best_score': best_score,
        'passed_count': passed_count,
        'failed_count': failed_count,
        'success_rate': round((passed_count / total_quizzes) * 100) if total_quizzes else 0,
        'total_time_display': total_time_display,
        'category_performance': category_performance,
    }
    return render(request, 'auth/profile.html', context)


@require_POST
def update_profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Giriş yapmalısınız.'}, status=401)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=400)

    full_name = str(payload.get('name', '')).strip()
    email = str(payload.get('email', '')).strip().lower()

    if not full_name or not email:
        return JsonResponse({'success': False, 'error': 'Ad soyad ve e-posta zorunludur.'}, status=400)

    if User.objects.exclude(pk=request.user.pk).filter(email=email).exists():
        return JsonResponse({'success': False, 'error': 'Bu e-posta başka bir kullanıcıda kayıtlı.'}, status=400)

    name_parts = full_name.split(' ', 1)
    request.user.first_name = name_parts[0]
    request.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
    request.user.email = email
    request.user.save(update_fields=['first_name', 'last_name', 'email'])

    return JsonResponse({
        'success': True,
        'user': {
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        },
    })


@require_POST
def change_password(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Giriş yapmalısınız.'}, status=401)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=400)

    current_password = str(payload.get('current_password', ''))
    new_password = str(payload.get('new_password', ''))
    confirm_password = str(payload.get('confirm_password', ''))

    if not request.user.check_password(current_password):
        return JsonResponse({'success': False, 'error': 'Mevcut şifre hatalı.'}, status=400)

    if len(new_password) < 6:
        return JsonResponse({'success': False, 'error': 'Yeni şifre en az 6 karakter olmalıdır.'}, status=400)

    if new_password != confirm_password:
        return JsonResponse({'success': False, 'error': 'Yeni şifreler eşleşmiyor.'}, status=400)

    request.user.set_password(new_password)
    request.user.save(update_fields=['password'])
    update_session_auth_hash(request, request.user)

    return JsonResponse({'success': True})


# ---------------------------------------------------------------------------
# Forgot Password
# ---------------------------------------------------------------------------

def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].lower()

        try:
            user = User.objects.get(email=email)
            otp  = OTPCode.create_for_user(user, OTPCode.PURPOSE_PASSWORD_RESET)
            _send_otp_email(user, otp)
        except User.DoesNotExist:
            pass  # E-posta numaralandırmasını önle

        request.session['reset_email'] = email
        return redirect('authentication:otp')

    return render(request, 'auth/forgot-password.html', {'form': form})


# ---------------------------------------------------------------------------
# OTP Doğrulama
# ---------------------------------------------------------------------------

def otp(request):
    reset_email = request.session.get('reset_email')
    if not reset_email:
        return redirect('authentication:forgot_password')

    form = OTPForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        code = form.cleaned_data['code']

        try:
            user    = User.objects.get(email=reset_email)
            otp_obj = OTPCode.objects.filter(
                user=user,
                purpose=OTPCode.PURPOSE_PASSWORD_RESET,
                is_used=False,
            ).latest('created_at')

            if not otp_obj.is_valid():
                form.add_error('code', 'Kodun süresi dolmuş. Lütfen tekrar e-posta gönderin.')
            elif otp_obj.code != code:
                form.add_error('code', 'Kod hatalı. Lütfen tekrar deneyin.')
            else:
                otp_obj.mark_used()
                request.session['reset_verified'] = True
                return redirect('authentication:set_new_password')

        except (User.DoesNotExist, OTPCode.DoesNotExist):
            form.add_error('code', 'Geçersiz kod. Lütfen tekrar deneyin.')

    return render(request, 'auth/otp.html', {'form': form})


# ---------------------------------------------------------------------------
# Set New Password
# ---------------------------------------------------------------------------

def set_new_password(request):
    reset_email    = request.session.get('reset_email')
    reset_verified = request.session.get('reset_verified')

    if not reset_email or not reset_verified:
        return redirect('authentication:forgot_password')

    form = SetNewPasswordForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        new_password = form.cleaned_data['new_password']

        try:
            user = User.objects.get(email=reset_email)
            user.set_password(new_password)
            user.save()

            request.session.pop('reset_email',    None)
            request.session.pop('reset_verified', None)

            messages.success(request, 'Şifren başarıyla güncellendi. Şimdi giriş yapabilirsin.')
            return redirect('authentication:login')

        except User.DoesNotExist:
            return redirect('authentication:forgot_password')

    return render(request, 'auth/set-new-password.html', {'form': form})
