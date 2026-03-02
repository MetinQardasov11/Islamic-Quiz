import random
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User modeli — email ile giriş yapılır.
    """
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    Kullanıcıya ait istatistik ve profil bilgileri.
    User kaydedildiğinde signal ile otomatik oluşturulur.
    """
    LEVEL_CHOICES = [
        (1, 'Acemi'),
        (2, 'Başlangıç'),
        (3, 'Orta'),
        (4, 'İleri'),
        (5, 'Uzman'),
    ]

    XP_THRESHOLDS = [0, 200, 600, 1_400, 3_000]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # XP & Seviye
    xp_points = models.PositiveIntegerField(default=0)
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=1)

    # Genel quiz istatistikleri
    total_score = models.PositiveIntegerField(default=0)
    total_quizzes_completed = models.PositiveIntegerField(default=0)
    total_correct_answers = models.PositiveIntegerField(default=0)
    total_questions_answered = models.PositiveIntegerField(default=0)

    # Gün serisi
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Kullanıcı Profili'
        verbose_name_plural = 'Kullanıcı Profilleri'

    def __str__(self):
        return f'{self.user.email} – Profil'

    # ------------------------------------------------------------------
    # Hesaplanan özellikler
    # ------------------------------------------------------------------

    @property
    def accuracy_rate(self):
        """Doğruluk oranı (%)"""
        if self.total_questions_answered == 0:
            return 0
        return round((self.total_correct_answers / self.total_questions_answered) * 100, 1)

    @property
    def xp_for_next_level(self):
        """Bir sonraki seviyeye gereken XP miktarı"""
        if self.level >= 5:
            return 0
        return self.XP_THRESHOLDS[self.level] - self.xp_points

    # ------------------------------------------------------------------
    # Yardımcı metodlar
    # ------------------------------------------------------------------

    def add_xp(self, amount: int):
        """XP ekle ve seviyeyi güncelle."""
        self.xp_points += amount
        self._recalculate_level()
        self.save(update_fields=['xp_points', 'level'])

    def _recalculate_level(self):
        new_level = 1
        for i, threshold in enumerate(self.XP_THRESHOLDS):
            if self.xp_points >= threshold:
                new_level = i + 1
        self.level = min(new_level, 5)

    def update_streak(self):
        """Her gün quiz tamamlandığında seriyi günceller."""
        today = timezone.localdate()
        if self.last_activity_date is None:
            self.current_streak = 1
        elif self.last_activity_date == today:
            return  # Bugün zaten güncellendi
        elif self.last_activity_date == today - timedelta(days=1):
            self.current_streak += 1
        else:
            self.current_streak = 1

        self.last_activity_date = today
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        self.save(update_fields=['current_streak', 'longest_streak', 'last_activity_date'])


class OTPCode(models.Model):
    """
    E-posta doğrulama ve şifre sıfırlama için 6 haneli OTP kodları.
    """
    PURPOSE_EMAIL_VERIFICATION = 'email_verification'
    PURPOSE_PASSWORD_RESET = 'password_reset'
    PURPOSE_CHOICES = [
        (PURPOSE_EMAIL_VERIFICATION, 'E-posta Doğrulama'),
        (PURPOSE_PASSWORD_RESET,     'Şifre Sıfırlama'),
    ]

    EXPIRY_MINUTES = 10

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'OTP Kodu'
        verbose_name_plural = 'OTP Kodları'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} – {self.get_purpose_display()} – {self.code}'

    def is_valid(self) -> bool:
        """Kodun süresi dolmamış ve kullanılmamış olduğunu kontrol eder."""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_used(self):
        self.is_used = True
        self.save(update_fields=['is_used'])

    @classmethod
    def create_for_user(cls, user: 'User', purpose: str) -> 'OTPCode':
        """
        Kullanıcı için yeni OTP oluşturur.
        Aynı amaç için bekleyen kodları önce geçersiz kılar.
        """
        cls.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)
        code = str(random.randint(100_000, 999_999))
        expires_at = timezone.now() + timedelta(minutes=cls.EXPIRY_MINUTES)
        return cls.objects.create(
            user=user,
            code=code,
            purpose=purpose,
            expires_at=expires_at,
        )
