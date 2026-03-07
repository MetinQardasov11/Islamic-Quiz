import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('base', '0002_quiz_models_and_seed_data'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='QuizCategory',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=120, unique=True, verbose_name='Kategori Adı')),
                        ('slug', models.SlugField(max_length=140, unique=True, verbose_name='Slug')),
                        ('description', models.TextField(blank=True, verbose_name='Açıklama')),
                        ('display_order', models.PositiveIntegerField(default=0, verbose_name='Sıra')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'verbose_name': 'Quiz Kategorisi',
                        'verbose_name_plural': 'Quiz Kategorileri',
                        'ordering': ['display_order', 'name'],
                        'db_table': 'base_quizcategory',
                    },
                ),
                migrations.CreateModel(
                    name='Quiz',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title', models.CharField(max_length=255, verbose_name='Quiz Başlığı')),
                        ('slug', models.SlugField(max_length=160, unique=True, verbose_name='Slug')),
                        ('description', models.TextField(verbose_name='Açıklama')),
                        ('difficulty', models.CharField(choices=[('easy', 'Kolay'), ('medium', 'Orta'), ('hard', 'Zor')], default='medium', max_length=20, verbose_name='Zorluk')),
                        ('subcategory', models.CharField(blank=True, max_length=120, verbose_name='Alt Kategori')),
                        ('thumbnail', models.URLField(blank=True, verbose_name='Kapak Görseli')),
                        ('time_limit', models.PositiveIntegerField(default=60, verbose_name='Süre Limiti (sn)')),
                        ('passing_score', models.PositiveIntegerField(default=70, verbose_name='Geçme Puanı (%)')),
                        ('display_order', models.PositiveIntegerField(default=0, verbose_name='Sıra')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quizzes', to='quiz.quizcategory', verbose_name='Kategori')),
                    ],
                    options={
                        'verbose_name': 'Quiz',
                        'verbose_name_plural': 'Quizler',
                        'ordering': ['display_order', 'title'],
                        'db_table': 'base_quiz',
                    },
                ),
                migrations.CreateModel(
                    name='MultiplayerSession',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('quiz_id', models.CharField(max_length=100, verbose_name='Quiz ID')),
                        ('quiz_title', models.CharField(max_length=255, verbose_name='Quiz Adı')),
                        ('player_one_name', models.CharField(max_length=50, verbose_name='Oyuncu 1')),
                        ('player_two_name', models.CharField(max_length=50, verbose_name='Oyuncu 2')),
                        ('player_one_score', models.PositiveIntegerField(default=0, verbose_name='Oyuncu 1 Skoru')),
                        ('player_two_score', models.PositiveIntegerField(default=0, verbose_name='Oyuncu 2 Skoru')),
                        ('total_questions', models.PositiveIntegerField(default=0, verbose_name='Toplam Soru')),
                        ('winner', models.CharField(blank=True, max_length=50, verbose_name='Kazanan')),
                        ('status', models.CharField(choices=[('completed', 'Tamamlandı'), ('time_up', 'Süre Doldu')], default='completed', max_length=20, verbose_name='Durum')),
                        ('played_at', models.DateTimeField(auto_now_add=True, verbose_name='Oynanma Tarihi')),
                        ('host', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='multiplayer_sessions', to=settings.AUTH_USER_MODEL, verbose_name='Ev Sahibi')),
                    ],
                    options={
                        'verbose_name': 'Çok Oyunculu Maç',
                        'verbose_name_plural': 'Çok Oyunculu Maçlar',
                        'ordering': ['-played_at'],
                        'db_table': 'base_multiplayersession',
                    },
                ),
                migrations.CreateModel(
                    name='QuizQuestion',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('question', models.TextField(verbose_name='Soru')),
                        ('options', models.JSONField(default=list, verbose_name='Seçenekler')),
                        ('correct_answer', models.PositiveSmallIntegerField(verbose_name='Doğru Cevap İndeksi')),
                        ('image', models.URLField(blank=True, verbose_name='Görsel URL')),
                        ('image_alt', models.CharField(blank=True, max_length=255, verbose_name='Görsel Alt Metni')),
                        ('image_caption', models.CharField(blank=True, max_length=255, verbose_name='Görsel Açıklaması')),
                        ('display_order', models.PositiveIntegerField(default=0, verbose_name='Sıra')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Aktif')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='quiz.quiz', verbose_name='Quiz')),
                    ],
                    options={
                        'verbose_name': 'Quiz Sorusu',
                        'verbose_name_plural': 'Quiz Soruları',
                        'ordering': ['display_order', 'id'],
                        'db_table': 'base_quizquestion',
                    },
                ),
            ],
        ),
    ]
