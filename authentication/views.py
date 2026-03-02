from django.shortcuts import render, redirect
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
)
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

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
    subject = 'QuizFlow — Şifre Sıfırlama Kodunuz'
    body = (
        f'Merhaba {user.first_name or user.username},\n\n'
        f'Şifre sıfırlama talebiniz için doğrulama kodunuz:\n\n'
        f'    {otp.code}\n\n'
        f'Bu kod {OTPCode.EXPIRY_MINUTES} dakika boyunca geçerlidir.\n'
        f'Eğer bu isteği siz yapmadıysanız bu e-postayı dikkate almayınız.\n\n'
        f'— QuizFlow Ekibi'
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
        return redirect('base:quizzes')

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
            next_url = request.GET.get('next') or 'base:quizzes'
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
    return render(request, 'auth/profile.html')


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
