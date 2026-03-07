from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, OTPCode


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_email_verified', 'is_staff', 'created_at')
    list_filter = ('is_email_verified', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Ek Bilgiler', {'fields': ('is_email_verified',)}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'xp_points', 'total_quizzes_completed', 'current_streak', 'accuracy_rate')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('accuracy_rate', 'xp_for_next_level', 'created_at', 'updated_at')


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'purpose', 'code', 'is_used', 'expires_at', 'created_at')
    search_fields = ('user__email', 'code')
    ordering = ('-created_at',)
