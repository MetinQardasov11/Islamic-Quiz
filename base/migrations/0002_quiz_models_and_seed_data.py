from django.db import migrations, models
import django.db.models.deletion


def seed_quiz_data(apps, schema_editor):
    # Seed intentionally disabled.
    # Local data can stay in the current database, but fresh environments
    # should not auto-import quiz content during migrate.
    return


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
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
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quizzes', to='base.quizcategory', verbose_name='Kategori')),
            ],
            options={
                'verbose_name': 'Quiz',
                'verbose_name_plural': 'Quizler',
                'ordering': ['display_order', 'title'],
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
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='base.quiz', verbose_name='Quiz')),
            ],
            options={
                'verbose_name': 'Quiz Sorusu',
                'verbose_name_plural': 'Quiz Soruları',
                'ordering': ['display_order', 'id'],
            },
        ),
        migrations.RunPython(seed_quiz_data, migrations.RunPython.noop),
    ]
