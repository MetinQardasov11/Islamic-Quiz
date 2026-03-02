from django.db import models
from django.conf import settings


class MultiplayerSession(models.Model):
    STATUS_COMPLETED = 'completed'
    STATUS_TIME_UP   = 'time_up'
    STATUS_CHOICES   = [
        (STATUS_COMPLETED, 'Tamamlandı'),
        (STATUS_TIME_UP,   'Süre Doldu'),
    ]

    host             = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='multiplayer_sessions',
        verbose_name='Ev Sahibi',
    )
    quiz_id          = models.CharField(max_length=100, verbose_name='Quiz ID')
    quiz_title       = models.CharField(max_length=255, verbose_name='Quiz Adı')
    player_one_name  = models.CharField(max_length=50, verbose_name='Oyuncu 1')
    player_two_name  = models.CharField(max_length=50, verbose_name='Oyuncu 2')
    player_one_score = models.PositiveIntegerField(default=0, verbose_name='Oyuncu 1 Skoru')
    player_two_score = models.PositiveIntegerField(default=0, verbose_name='Oyuncu 2 Skoru')
    total_questions  = models.PositiveIntegerField(default=0, verbose_name='Toplam Soru')
    winner           = models.CharField(max_length=50, blank=True, verbose_name='Kazanan')
    status           = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_COMPLETED,
        verbose_name='Durum',
    )
    played_at        = models.DateTimeField(auto_now_add=True, verbose_name='Oynanma Tarihi')

    class Meta:
        verbose_name        = 'Çok Oyunculu Maç'
        verbose_name_plural = 'Çok Oyunculu Maçlar'
        ordering            = ['-played_at']

    def __str__(self):
        return f'{self.player_one_name} vs {self.player_two_name} — {self.quiz_title}'
