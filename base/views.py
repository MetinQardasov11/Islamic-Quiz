from django.shortcuts import render

from content.models import FAQItem, HomeFeature, HomeStat, SiteSettings, TermsItem


def index(request):
    site_settings = SiteSettings.objects.order_by('id').first()
    context = {
        'site_settings': site_settings,
        'home_features': HomeFeature.objects.filter(is_active=True).order_by('display_order', 'id'),
        'home_stats': HomeStat.objects.filter(is_active=True).order_by('display_order', 'id'),
        'home_faq_items': FAQItem.objects.filter(is_active=True, show_on_homepage=True).order_by('display_order', 'id')[:2],
        'home_terms_items': TermsItem.objects.filter(is_active=True, show_on_homepage=True).order_by('display_order', 'id')[:2],
    }
    return render(request, 'base/index.html', context)


def faq(request):
    site_settings = SiteSettings.objects.order_by('id').first()
    context = {
        'site_settings': site_settings,
        'faq_items': FAQItem.objects.filter(is_active=True).order_by('display_order', 'id'),
    }
    return render(request, 'base/faq.html', context)


def terms_of_use(request):
    site_settings = SiteSettings.objects.order_by('id').first()
    context = {
        'site_settings': site_settings,
        'terms_items': TermsItem.objects.filter(is_active=True).order_by('display_order', 'id'),
    }
    return render(request, 'base/terms-of-use.html', context)


def page_not_found(request):
    return render(request, 'base/404.html', status=404)
