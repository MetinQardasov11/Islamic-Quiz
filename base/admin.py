from django.contrib import admin
from .models import MultiplayerSession


@admin.register(MultiplayerSession)
class MultiplayerSessionAdmin(admin.ModelAdmin):
    list_display  = ('player_one_name', 'player_two_name', 'quiz_title', 'player_one_score', 'player_two_score', 'winner', 'status', 'host', 'played_at')
    list_filter   = ('status', 'played_at')
    search_fields = ('player_one_name', 'player_two_name', 'quiz_title', 'host__email')
    readonly_fields = ('played_at',)
