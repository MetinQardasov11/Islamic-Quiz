from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.index, name='index'),
    path('faq/', views.faq, name='faq'),
    path('terms/', views.terms_of_use, name='terms_of_use'),
    path('404/', views.page_not_found, name='page_not_found'),
]
