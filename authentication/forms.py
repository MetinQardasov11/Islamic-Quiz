from django import forms
from .models import User


class RegisterForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        error_messages={'required': 'Ad Soyad boş olamaz.'},
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ahmet Yılmaz',
            'id': 'name',
        }),
    )
    email = forms.EmailField(
        error_messages={
            'required': 'E-posta boş olamaz.',
            'invalid': 'Geçerli bir e-posta adresi girin.',
        },
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ornek@mail.com',
            'id': 'email',
        }),
    )
    password = forms.CharField(
        min_length=6,
        error_messages={
            'required': 'Şifre boş olamaz.',
            'min_length': 'Şifre en az 6 karakter olmalıdır.',
        },
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'En az 6 karakter',
            'minlength': '6',
            'id': 'password',
        }),
    )
    confirm_password = forms.CharField(
        min_length=6,
        error_messages={'required': 'Şifreyi tekrar girin.'},
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şifreyi tekrar gir',
            'minlength': '6',
            'id': 'confirmPassword',
        }),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Bu e-posta adresi zaten kayıtlı.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm  = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            self.add_error('confirm_password', 'Şifreler eşleşmiyor.')
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        error_messages={
            'required': 'E-posta boş olamaz.',
            'invalid': 'Geçerli bir e-posta adresi girin.',
        },
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ornek@mail.com',
            'id': 'email',
        }),
    )
    password = forms.CharField(
        error_messages={'required': 'Şifre boş olamaz.'},
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şifreni gir',
            'id': 'password',
        }),
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'id': 'rememberMe'}),
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        error_messages={
            'required': 'E-posta boş olamaz.',
            'invalid': 'Geçerli bir e-posta adresi girin.',
        },
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ornek@mail.com',
            'id': 'email',
        }),
    )


class OTPForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        error_messages={
            'required': 'Doğrulama kodu boş olamaz.',
            'min_length': '6 haneli kodu eksiksiz girin.',
            'max_length': '6 haneli kodu eksiksiz girin.',
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123456',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'maxlength': '6',
            'autocomplete': 'one-time-code',
            'id': 'otpCode',
        }),
    )

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip()
        if not code.isdigit():
            raise forms.ValidationError('Kod yalnızca rakamlardan oluşmalıdır.')
        return code


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        min_length=6,
        error_messages={
            'required': 'Yeni şifre boş olamaz.',
            'min_length': 'Şifre en az 6 karakter olmalıdır.',
        },
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Yeni şifreni gir',
            'minlength': '6',
            'id': 'newPassword',
        }),
    )
    confirm_new_password = forms.CharField(
        min_length=6,
        error_messages={'required': 'Şifreyi tekrar girin.'},
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Yeni şifreni tekrar gir',
            'minlength': '6',
            'id': 'confirmNewPassword',
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm      = cleaned_data.get('confirm_new_password')
        if new_password and confirm and new_password != confirm:
            self.add_error('confirm_new_password', 'Şifreler eşleşmiyor.')
        return cleaned_data
