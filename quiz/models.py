from django.conf import settings
from django.db import models


class QuizCategory(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name='Kategori Adı')
    slug = models.SlugField(max_length=140, unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    display_order = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Quiz Kategorisi'
        verbose_name_plural = 'Quiz Kategorileri'
        ordering = ['display_order', 'name']
        db_table = 'base_quizcategory'

    def __str__(self):
        return self.name


class Quiz(models.Model):
    DIFFICULTY_EASY = 'easy'
    DIFFICULTY_MEDIUM = 'medium'
    DIFFICULTY_HARD = 'hard'
    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY, 'Kolay'),
        (DIFFICULTY_MEDIUM, 'Orta'),
        (DIFFICULTY_HARD, 'Zor'),
    ]

    category = models.ForeignKey(
        QuizCategory,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name='Kategori',
    )
    title = models.CharField(max_length=255, verbose_name='Quiz Başlığı')
    slug = models.SlugField(max_length=160, unique=True, verbose_name='Slug')
    description = models.TextField(verbose_name='Açıklama')
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default=DIFFICULTY_MEDIUM,
        verbose_name='Zorluk',
    )
    subcategory = models.CharField(max_length=120, blank=True, verbose_name='Alt Kategori')
    thumbnail = models.URLField(blank=True, verbose_name='Kapak Görseli')
    thumbnail_file = models.FileField(
        upload_to='quiz/thumbnails/',
        blank=True,
        verbose_name='Kapak Görsel Dosyası',
    )
    time_limit = models.PositiveIntegerField(default=60, verbose_name='Süre Limiti (sn)')
    passing_score = models.PositiveIntegerField(default=70, verbose_name='Geçme Puanı (%)')
    display_order = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizler'
        ordering = ['display_order', 'title']
        db_table = 'base_quiz'

    def __str__(self):
        return self.title

    @property
    def thumbnail_url(self):
        if self.thumbnail_file:
            return self.thumbnail_file.url
        return self.thumbnail


class QuizQuestion(models.Model):
    TYPE_TEXT_QUESTION_TEXT_ANSWERS = 'text_question_text_answers'
    TYPE_IMAGE_QUESTION_TEXT_ANSWERS = 'image_question_text_answers'
    TYPE_TEXT_QUESTION_IMAGE_ANSWERS = 'text_question_image_answers'
    TYPE_IMAGE_QUESTION_IMAGE_ANSWERS = 'image_question_image_answers'
    QUESTION_TYPE_CHOICES = [
        (TYPE_TEXT_QUESTION_TEXT_ANSWERS, 'Metin soru + metin cevaplar'),
        (TYPE_IMAGE_QUESTION_TEXT_ANSWERS, 'Resimli soru + metin cevaplar'),
        (TYPE_TEXT_QUESTION_IMAGE_ANSWERS, 'Metin soru + resimli cevaplar'),
        (TYPE_IMAGE_QUESTION_IMAGE_ANSWERS, 'Resimli soru + resimli cevaplar'),
    ]

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Quiz',
    )
    question_type = models.CharField(
        max_length=40,
        choices=QUESTION_TYPE_CHOICES,
        default=TYPE_TEXT_QUESTION_TEXT_ANSWERS,
        verbose_name='Soru Tipi',
    )
    question = models.TextField(verbose_name='Soru')
    options = models.JSONField(default=list, verbose_name='Seçenekler')
    correct_answer = models.PositiveSmallIntegerField(verbose_name='Doğru Cevap İndeksi')
    image = models.URLField(blank=True, verbose_name='Görsel URL')
    image_file = models.FileField(
        upload_to='quiz/questions/',
        blank=True,
        verbose_name='Görsel Dosyası',
    )
    image_alt = models.CharField(max_length=255, blank=True, verbose_name='Görsel Alt Metni')
    image_caption = models.CharField(max_length=255, blank=True, verbose_name='Görsel Açıklaması')
    display_order = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Quiz Sorusu'
        verbose_name_plural = 'Quiz Soruları'
        ordering = ['display_order', 'id']
        db_table = 'base_quizquestion'

    def __str__(self):
        return f'{self.quiz.title} - Soru {self.display_order or self.pk}'

    @property
    def uses_question_image(self):
        return self.question_type in {
            self.TYPE_IMAGE_QUESTION_TEXT_ANSWERS,
            self.TYPE_IMAGE_QUESTION_IMAGE_ANSWERS,
        }

    @property
    def uses_answer_images(self):
        return self.question_type in {
            self.TYPE_TEXT_QUESTION_IMAGE_ANSWERS,
            self.TYPE_IMAGE_QUESTION_IMAGE_ANSWERS,
        }

    @property
    def image_url(self):
        if self.image_file:
            return self.image_file.url
        return self.image


class QuizAnswerOption(models.Model):
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='answer_options',
        verbose_name='Soru',
    )
    text = models.CharField(max_length=255, blank=True, verbose_name='Cevap Metni')
    image = models.URLField(blank=True, verbose_name='Cevap Görseli')
    image_file = models.FileField(
        upload_to='quiz/answers/',
        blank=True,
        verbose_name='Cevap Görsel Dosyası',
    )
    image_alt = models.CharField(max_length=255, blank=True, verbose_name='Cevap Görsel Alt Metni')
    is_correct = models.BooleanField(default=False, verbose_name='Doğru Cevap')
    display_order = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cevap Şıkkı'
        verbose_name_plural = 'Cevap Şıkları'
        ordering = ['display_order', 'id']

    def __str__(self):
        return f'{self.question} - Şık {self.display_order + 1}'

    @property
    def image_url(self):
        if self.image_file:
            return self.image_file.url
        return self.image


class MultiplayerSession(models.Model):
    STATUS_COMPLETED = 'completed'
    STATUS_TIME_UP = 'time_up'
    STATUS_CHOICES = [
        (STATUS_COMPLETED, 'Tamamlandı'),
        (STATUS_TIME_UP, 'Süre Doldu'),
    ]

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='multiplayer_sessions',
        verbose_name='Ev Sahibi',
    )
    quiz_id = models.CharField(max_length=100, verbose_name='Quiz ID')
    quiz_title = models.CharField(max_length=255, verbose_name='Quiz Adı')
    player_one_name = models.CharField(max_length=50, verbose_name='Oyuncu 1')
    player_two_name = models.CharField(max_length=50, verbose_name='Oyuncu 2')
    player_one_score = models.PositiveIntegerField(default=0, verbose_name='Oyuncu 1 Skoru')
    player_two_score = models.PositiveIntegerField(default=0, verbose_name='Oyuncu 2 Skoru')
    total_questions = models.PositiveIntegerField(default=0, verbose_name='Toplam Soru')
    winner = models.CharField(max_length=50, blank=True, verbose_name='Kazanan')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_COMPLETED,
        verbose_name='Durum',
    )
    played_at = models.DateTimeField(auto_now_add=True, verbose_name='Oynanma Tarihi')

    class Meta:
        verbose_name = 'Çok Oyunculu Maç'
        verbose_name_plural = 'Çok Oyunculu Maçlar'
        ordering = ['-played_at']
        db_table = 'base_multiplayersession'

    def __str__(self):
        return f'{self.player_one_name} vs {self.player_two_name} — {self.quiz_title}'


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name='Kullanıcı',
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Quiz',
    )
    correct_count = models.PositiveIntegerField(default=0, verbose_name='Doğru Sayısı')
    total_questions = models.PositiveIntegerField(default=0, verbose_name='Toplam Soru')
    percentage = models.PositiveIntegerField(default=0, verbose_name='Yüzde Skor')
    passed = models.BooleanField(default=False, verbose_name='Geçti')
    elapsed_seconds = models.PositiveIntegerField(default=0, verbose_name='Geçen Süre')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Tamamlanma Tarihi')

    class Meta:
        verbose_name = 'Quiz Denemesi'
        verbose_name_plural = 'Quiz Denemeleri'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.quiz} - %{self.percentage}'


class QuizAttemptAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Deneme',
    )
    question_order = models.PositiveIntegerField(default=0, verbose_name='Soru Sırası')
    question_text = models.TextField(verbose_name='Soru Metni')
    selected_answer_index = models.IntegerField(null=True, blank=True, verbose_name='Seçilen Cevap İndeksi')
    selected_answer_text = models.CharField(max_length=255, blank=True, verbose_name='Seçilen Cevap')
    selected_answer_image = models.URLField(blank=True, verbose_name='Seçilen Cevap Görseli')
    selected_answer_image_alt = models.CharField(max_length=255, blank=True, verbose_name='Seçilen Cevap Görsel Alt')
    correct_answer_index = models.PositiveIntegerField(verbose_name='Doğru Cevap İndeksi')
    correct_answer_text = models.CharField(max_length=255, verbose_name='Doğru Cevap')
    correct_answer_image = models.URLField(blank=True, verbose_name='Doğru Cevap Görseli')
    correct_answer_image_alt = models.CharField(max_length=255, blank=True, verbose_name='Doğru Cevap Görsel Alt')
    is_correct = models.BooleanField(default=False, verbose_name='Doğru mu')
    image = models.URLField(blank=True, verbose_name='Görsel URL')
    image_alt = models.CharField(max_length=255, blank=True, verbose_name='Görsel Alt')
    image_caption = models.CharField(max_length=255, blank=True, verbose_name='Görsel Açıklama')

    class Meta:
        verbose_name = 'Deneme Cevabı'
        verbose_name_plural = 'Deneme Cevapları'
        ordering = ['question_order', 'id']

    def __str__(self):
        return f'{self.attempt} - Soru {self.question_order + 1}'
