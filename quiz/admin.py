from django import forms
from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import MultiplayerSession, Quiz, QuizAnswerOption, QuizAttempt, QuizAttemptAnswer, QuizCategory, QuizQuestion


class ImageSourceAdminFormMixin:
    IMAGE_SOURCE_URL = 'url'
    IMAGE_SOURCE_FILE = 'file'
    IMAGE_SOURCE_CHOICES = [
        (IMAGE_SOURCE_URL, 'URL kullan'),
        (IMAGE_SOURCE_FILE, 'Dosya yukle'),
    ]

    def configure_image_source_field(self, field_name, file_field_name, selector_field_name):
        self.fields[selector_field_name].initial = (
            self.IMAGE_SOURCE_FILE if getattr(self.instance, file_field_name, None) else self.IMAGE_SOURCE_URL
        )
        self.fields[selector_field_name].widget.attrs.update({
            'data-image-source-selector': 'true',
            'data-image-target': field_name,
            'data-image-file-target': file_field_name,
        })
        self.fields[file_field_name].widget.attrs.update({'accept': 'image/*'})
        self.fields[field_name].widget.attrs.update({'placeholder': 'https://ornek.com/gorsel.jpg'})


class QuizAdminForm(ImageSourceAdminFormMixin, forms.ModelForm):
    thumbnail_source_mode = forms.ChoiceField(
        choices=ImageSourceAdminFormMixin.IMAGE_SOURCE_CHOICES,
        initial=ImageSourceAdminFormMixin.IMAGE_SOURCE_URL,
        required=False,
        label='Kapak Görsel Kaynağı',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure_image_source_field('thumbnail', 'thumbnail_file', 'thumbnail_source_mode')

    class Meta:
        model = Quiz
        fields = '__all__'


class QuizQuestionAdminForm(ImageSourceAdminFormMixin, forms.ModelForm):
    image_source_mode = forms.ChoiceField(
        choices=ImageSourceAdminFormMixin.IMAGE_SOURCE_CHOICES,
        initial=ImageSourceAdminFormMixin.IMAGE_SOURCE_URL,
        required=False,
        label='Görsel Kaynağı',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['options'].required = False
        self.fields['correct_answer'].required = False
        self.configure_image_source_field('image', 'image_file', 'image_source_mode')
        self.fields['question'].widget.attrs.update({
            'rows': 3,
            'placeholder': 'Soruyu buraya yazın.',
        })
        self.fields['image'].widget.attrs.update({'placeholder': 'https://ornek.com/soru-gorseli.jpg'})
        self.fields['image_alt'].widget.attrs.update({
            'placeholder': 'Gorsel aciklamasi',
        })
        self.fields['image_caption'].widget.attrs.update({
            'placeholder': 'Istege bagli kisa aciklama',
        })

    def clean(self):
        cleaned_data = super().clean()
        question_type = cleaned_data.get('question_type')
        image = (cleaned_data.get('image') or '').strip()
        image_file = cleaned_data.get('image_file')
        image_source_mode = cleaned_data.get('image_source_mode') or self.IMAGE_SOURCE_URL

        cleaned_data['options'] = []
        cleaned_data['correct_answer'] = 0

        if question_type in {
            QuizQuestion.TYPE_IMAGE_QUESTION_TEXT_ANSWERS,
            QuizQuestion.TYPE_IMAGE_QUESTION_IMAGE_ANSWERS,
        }:
            if image_source_mode == self.IMAGE_SOURCE_FILE and not image_file:
                self.add_error('image_file', 'Bu soru tipinde bir görsel dosyası yüklemelisiniz.')
            if image_source_mode == self.IMAGE_SOURCE_URL and not image:
                self.add_error('image', 'Bu soru tipinde bir görsel URL girmelisiniz.')

        return cleaned_data

    class Meta:
        model = QuizQuestion
        fields = '__all__'
        widgets = {
            'options': forms.HiddenInput(),
            'correct_answer': forms.HiddenInput(),
        }


class QuizAnswerOptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        question_type = self.data.get(
            'question_type',
            getattr(self.instance, 'question_type', QuizQuestion.TYPE_TEXT_QUESTION_TEXT_ANSWERS),
        )
        uses_answer_images = question_type in {
            QuizQuestion.TYPE_TEXT_QUESTION_IMAGE_ANSWERS,
            QuizQuestion.TYPE_IMAGE_QUESTION_IMAGE_ANSWERS,
        }

        active_forms = []
        correct_count = 0

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue

            cleaned_data = form.cleaned_data
            if cleaned_data.get('DELETE'):
                continue

            text = (cleaned_data.get('text') or '').strip()
            image = (cleaned_data.get('image') or '').strip()
            image_file = cleaned_data.get('image_file')
            image_source_mode = cleaned_data.get('image_source_mode') or QuizQuestionAdminForm.IMAGE_SOURCE_URL
            is_active = cleaned_data.get('is_active', True)

            if not text and not image and not image_file and not is_active:
                continue

            if not text and not image and not image_file:
                raise forms.ValidationError('Her şık için en az bir metin veya görsel girilmelidir.')

            if uses_answer_images:
                if image_source_mode == QuizQuestionAdminForm.IMAGE_SOURCE_FILE and not image_file:
                    raise forms.ValidationError('Dosya seçiliyse her cevap şıkkında bir görsel dosyası yüklenmelidir.')
                if image_source_mode == QuizQuestionAdminForm.IMAGE_SOURCE_URL and not image:
                    raise forms.ValidationError('URL seçiliyse her cevap şıkkında bir görsel URL girilmelidir.')

            if not uses_answer_images and not text:
                raise forms.ValidationError('Seçilen soru tipinde tüm cevap şıklarında metin zorunludur.')

            if cleaned_data.get('is_correct'):
                correct_count += 1

            if is_active:
                active_forms.append(form)

        if len(active_forms) < 2:
            raise forms.ValidationError('Bir soru için en az iki aktif cevap şıkkı eklenmelidir.')

        if correct_count != 1:
            raise forms.ValidationError('Bir soru için tam olarak bir doğru cevap seçilmelidir.')


class QuizAnswerOptionInlineForm(ImageSourceAdminFormMixin, forms.ModelForm):
    image_source_mode = forms.ChoiceField(
        choices=QuizQuestionAdminForm.IMAGE_SOURCE_CHOICES,
        initial=QuizQuestionAdminForm.IMAGE_SOURCE_URL,
        required=False,
        label='Görsel Kaynağı',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure_image_source_field('image', 'image_file', 'image_source_mode')
        self.fields['text'].widget.attrs.update({
            'placeholder': 'Cevap metni',
        })
        self.fields['image'].widget.attrs.update({'placeholder': 'https://ornek.com/cevap-gorseli.jpg'})
        self.fields['image_alt'].widget.attrs.update({
            'placeholder': 'Cevap gorsel aciklamasi',
        })

    class Meta:
        model = QuizAnswerOption
        fields = '__all__'


class QuizAnswerOptionInline(admin.StackedInline):
    model = QuizAnswerOption
    form = QuizAnswerOptionInlineForm
    formset = QuizAnswerOptionInlineFormSet
    extra = 4
    verbose_name = 'Cevap Şıkkı'
    verbose_name_plural = 'Cevap Şıkları'
    fields = (
        ('display_order', 'is_correct', 'is_active'),
        'image_source_mode',
        'text',
        ('image', 'image_file'),
        'image_alt',
    )
    ordering = ('display_order', 'id')
    classes = ('quiz-answer-option-inline',)


@admin.register(QuizCategory)
class QuizCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm
    list_display = ('title', 'category', 'difficulty', 'subcategory', 'time_limit', 'display_order', 'is_active', 'question_count')
    list_filter = ('category', 'difficulty', 'is_active')
    search_fields = ('title', 'slug', 'description', 'subcategory')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('display_order', 'title')
    fields = (
        'category',
        'title',
        'slug',
        'description',
        ('difficulty', 'subcategory'),
        'thumbnail_source_mode',
        'thumbnail_file',
        'thumbnail',
        ('time_limit', 'passing_score'),
        ('display_order', 'is_active'),
    )

    def question_count(self, obj):
        return obj.questions.count()

    question_count.short_description = 'Soru Sayısı'

    class Media:
        js = ('admin/js/shared-image-source-admin.js',)
        css = {
            'all': ('admin/css/shared-image-source-admin.css',),
        }


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    form = QuizQuestionAdminForm
    list_display = ('quiz', 'display_order', 'question_type', 'is_active', 'option_count')
    list_filter = ('quiz', 'question_type', 'is_active')
    search_fields = ('quiz__title', 'question')
    ordering = ('quiz', 'display_order', 'id')
    fieldsets = (
        ('Genel Bilgiler', {
            'fields': (
                ('quiz', 'display_order', 'is_active'),
                'question_type',
                'question',
            ),
        }),
        ('Soru Görseli', {
            'fields': (
                'image_source_mode',
                'image',
                'image_file',
                ('image_alt', 'image_caption'),
            ),
            'description': 'Yalnızca resimli soru tiplerinde zorunludur.',
        }),
        ('Uyumluluk Alanlari', {
            'classes': ('hidden-compat-fields',),
            'fields': ('options', 'correct_answer'),
        }),
    )
    inlines = [QuizAnswerOptionInline]

    def option_count(self, obj):
        return obj.answer_options.count()

    option_count.short_description = 'Şık Sayısı'

    class Media:
        js = ('admin/js/shared-image-source-admin.js', 'admin/js/quiz-question-admin.js',)
        css = {
            'all': ('admin/css/shared-image-source-admin.css', 'admin/css/quiz-question-admin.css'),
        }


@admin.register(MultiplayerSession)
class MultiplayerSessionAdmin(admin.ModelAdmin):
    list_display = ('player_one_name', 'player_two_name', 'quiz_title', 'player_one_score', 'player_two_score', 'winner', 'status', 'host', 'played_at')
    list_filter = ('status', 'played_at')
    search_fields = ('player_one_name', 'player_two_name', 'quiz_title', 'host__email')
    readonly_fields = ('played_at',)


class QuizAttemptAnswerInline(admin.TabularInline):
    model = QuizAttemptAnswer
    extra = 0
    can_delete = False
    base_fields = (
        'question_order',
        'question_text',
        'selected_answer_index',
        'selected_answer_text',
        'correct_answer_index',
        'correct_answer_text',
        'is_correct',
    )
    optional_field_checks = (
        ('selected_answer_image', 'selected_answer_image'),
        ('selected_answer_image_alt', 'selected_answer_image_alt'),
        ('correct_answer_image', 'correct_answer_image'),
        ('correct_answer_image_alt', 'correct_answer_image_alt'),
        ('image', 'image'),
        ('image_alt', 'image_alt'),
        ('image_caption', 'image_caption'),
    )

    def get_fields(self, request, obj=None):
        fields = list(self.base_fields)
        if not obj:
            return fields

        answers = obj.answers.all()
        for field_name, lookup in self.optional_field_checks:
            if answers.exclude(**{lookup: ''}).exists():
                fields.append(field_name)
        return fields

    def get_readonly_fields(self, request, obj=None):
        return self.get_fields(request, obj)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'correct_count', 'total_questions', 'percentage', 'passed', 'elapsed_seconds', 'created_at')
    list_filter = ('passed', 'quiz__category', 'quiz')
    search_fields = ('user__email', 'user__username', 'quiz__title')
    readonly_fields = ('created_at',)
    inlines = [QuizAttemptAnswerInline]
