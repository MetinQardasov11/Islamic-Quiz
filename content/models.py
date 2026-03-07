from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=120, default='QuizFlow', verbose_name='Site Adı')
    site_logo = models.URLField(blank=True, verbose_name='Site Logo URL')
    site_logo_file = models.FileField(
        upload_to='content/site/',
        blank=True,
        verbose_name='Site Logo Dosyası',
    )
    footer_meta = models.CharField(max_length=255, default='QuizFlow (c) 2026', verbose_name='Footer Meta')
    footer_copy = models.CharField(max_length=255, default='Bilgini güçlendiren modern quiz deneyimi.', verbose_name='Varsayılan Footer Metni')
    hero_title = models.CharField(max_length=255, default='Bilgini sadece ölçme, hikâyeye dönüştür', verbose_name='Ana Sayfa Başlığı')
    hero_description = models.TextField(blank=True, verbose_name='Ana Sayfa Açıklaması')
    hero_image = models.URLField(blank=True, verbose_name='Hero Görsel URL')
    hero_image_file = models.FileField(
        upload_to='content/hero/',
        blank=True,
        verbose_name='Hero Görsel Dosyası',
    )
    faq_page_title = models.CharField(max_length=255, default='Sıkça Sorulan Sorular', verbose_name='SSS Başlığı')
    faq_page_description = models.TextField(blank=True, verbose_name='SSS Açıklaması')
    terms_page_title = models.CharField(max_length=255, default='Kullanım Şartları', verbose_name='Şartlar Başlığı')
    terms_page_description = models.TextField(blank=True, verbose_name='Şartlar Açıklaması')
    terms_note_prefix = models.CharField(max_length=255, blank=True, verbose_name='Şartlar Not Ön Ek')
    terms_note_link_label = models.CharField(max_length=120, blank=True, verbose_name='Şartlar Not Link Yazısı')
    terms_note_link_url = models.CharField(max_length=255, blank=True, verbose_name='Şartlar Not Link URL')
    terms_note_suffix = models.CharField(max_length=255, blank=True, verbose_name='Şartlar Not Son Ek')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Ayarı'
        verbose_name_plural = 'Site Ayarları'

    def __str__(self):
        return self.site_name

    @property
    def site_logo_url(self):
        if self.site_logo_file:
            return self.site_logo_file.url
        return self.site_logo

    @property
    def hero_image_url(self):
        if self.hero_image_file:
            return self.hero_image_file.url
        return self.hero_image


class SocialLink(models.Model):
    label = models.CharField(max_length=80, verbose_name='Ad')
    url = models.URLField(verbose_name='URL')
    icon_class = models.CharField(max_length=80, default='ph ph-link', verbose_name='İkon Sınıfı')
    display_order = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Sosyal Medya Linki'
        verbose_name_plural = 'Sosyal Medya Linkleri'
        ordering = ['display_order', 'label']

    def __str__(self):
        return self.label


class FAQItem(models.Model):
    question = models.CharField(max_length=255, verbose_name='Soru')
    answer = models.TextField(verbose_name='Cevap')
    display_order = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    show_on_homepage = models.BooleanField(default=True, verbose_name='Ana Sayfada Göster')

    class Meta:
        verbose_name = 'SSS Maddesi'
        verbose_name_plural = 'SSS Maddeleri'
        ordering = ['display_order', 'id']

    def __str__(self):
        return self.question


class TermsItem(models.Model):
    title = models.CharField(max_length=255, verbose_name='Başlık')
    description = models.TextField(verbose_name='Açıklama')
    display_order = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    show_on_homepage = models.BooleanField(default=True, verbose_name='Ana Sayfada Göster')

    class Meta:
        verbose_name = 'Şart Maddesi'
        verbose_name_plural = 'Şart Maddeleri'
        ordering = ['display_order', 'id']

    def __str__(self):
        return self.title


class HomeFeature(models.Model):
    title = models.CharField(max_length=255, verbose_name='Başlık')
    description = models.TextField(verbose_name='Açıklama')
    image = models.URLField(blank=True, verbose_name='Görsel URL')
    image_file = models.FileField(
        upload_to='content/features/',
        blank=True,
        verbose_name='Görsel Dosyası',
    )
    display_order = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Ana Sayfa Özelliği'
        verbose_name_plural = 'Ana Sayfa Özellikleri'
        ordering = ['display_order', 'id']

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image_file:
            return self.image_file.url
        return self.image


class HomeStat(models.Model):
    icon_class = models.CharField(max_length=80, default='ph ph-chart-bar', verbose_name='İkon Sınıfı')
    value = models.CharField(max_length=80, verbose_name='Değer')
    label = models.CharField(max_length=120, verbose_name='Etiket')
    display_order = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')

    class Meta:
        verbose_name = 'Ana Sayfa İstatistiği'
        verbose_name_plural = 'Ana Sayfa İstatistikleri'
        ordering = ['display_order', 'id']

    def __str__(self):
        return self.label
