from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/',            views.login,            name='login'),
    path('register/',         views.register,         name='register'),
    path('logout/',           views.logout,           name='logout'),
    path('profile/',          views.profile,          name='profile'),
    path('api/profile/update/', views.update_profile, name='update_profile'),
    path('api/profile/change-password/', views.change_password, name='change_password'),
    path('forgot-password/',  views.forgot_password,  name='forgot_password'),
    path('otp/',              views.otp,              name='otp'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),
]
