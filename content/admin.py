from django import forms
from django.contrib import admin

from .models import FAQItem, HomeFeature, HomeStat, SiteSettings, SocialLink, TermsItem


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


class SiteSettingsAdminForm(ImageSourceAdminFormMixin, forms.ModelForm):
    site_logo_source_mode = forms.ChoiceField(
        choices=ImageSourceAdminFormMixin.IMAGE_SOURCE_CHOICES,
        initial=ImageSourceAdminFormMixin.IMAGE_SOURCE_URL,
        required=False,
        label='Logo Kaynağı',
    )
    hero_image_source_mode = forms.ChoiceField(
        choices=ImageSourceAdminFormMixin.IMAGE_SOURCE_CHOICES,
        initial=ImageSourceAdminFormMixin.IMAGE_SOURCE_URL,
        required=False,
        label='Hero Görsel Kaynağı',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure_image_source_field('site_logo', 'site_logo_file', 'site_logo_source_mode')
        self.configure_image_source_field('hero_image', 'hero_image_file', 'hero_image_source_mode')

    class Meta:
        model = SiteSettings
        fields = '__all__'


class HomeFeatureAdminForm(ImageSourceAdminFormMixin, forms.ModelForm):
    image_source_mode = forms.ChoiceField(
        choices=ImageSourceAdminFormMixin.IMAGE_SOURCE_CHOICES,
        initial=ImageSourceAdminFormMixin.IMAGE_SOURCE_URL,
        required=False,
        label='Görsel Kaynağı',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure_image_source_field('image', 'image_file', 'image_source_mode')

    class Meta:
        model = HomeFeature
        fields = '__all__'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsAdminForm
    list_display = ('site_name', 'footer_meta', 'updated_at')
    fieldsets = (
        ('Genel', {
            'fields': (
                'site_name',
                ('footer_meta', 'footer_copy'),
            ),
        }),
        ('Logo', {
            'fields': (
                'site_logo_source_mode',
                'site_logo_file',
                'site_logo',
            ),
        }),
        ('Ana Sayfa Hero', {
            'fields': (
                'hero_title',
                'hero_description',
                'hero_image_source_mode',
                'hero_image_file',
                'hero_image',
            ),
        }),
        ('Bilgi Sayfalari', {
            'fields': (
                ('faq_page_title', 'terms_page_title'),
                ('faq_page_description', 'terms_page_description'),
                ('terms_note_prefix', 'terms_note_link_label'),
                ('terms_note_link_url', 'terms_note_suffix'),
            ),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    class Media:
        js = ('admin/js/shared-image-source-admin.js',)
        css = {
            'all': ('admin/css/shared-image-source-admin.css',),
        }


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('label', 'url', 'display_order', 'is_active')
    list_filter = ('is_active',)
    ordering = ('display_order', 'label')


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ('question', 'display_order', 'show_on_homepage', 'is_active')
    list_filter = ('show_on_homepage', 'is_active')
    ordering = ('display_order', 'id')


@admin.register(TermsItem)
class TermsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_order', 'show_on_homepage', 'is_active')
    list_filter = ('show_on_homepage', 'is_active')
    ordering = ('display_order', 'id')


@admin.register(HomeFeature)
class HomeFeatureAdmin(admin.ModelAdmin):
    form = HomeFeatureAdminForm
    list_display = ('title', 'display_order', 'is_active')
    list_filter = ('is_active',)
    ordering = ('display_order', 'id')
    fields = (
        'title',
        'description',
        'image_source_mode',
        'image_file',
        'image',
        ('display_order', 'is_active'),
    )

    class Media:
        js = ('admin/js/shared-image-source-admin.js',)
        css = {
            'all': ('admin/css/shared-image-source-admin.css',),
        }


@admin.register(HomeStat)
class HomeStatAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'display_order', 'is_active')
    list_filter = ('is_active',)
    ordering = ('display_order', 'id')
