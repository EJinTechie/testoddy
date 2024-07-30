from django.contrib import admin
from .models import Profile, Game, Card, GameStatus, CardSelection

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'score')
    search_fields = ('user__username',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('attacker', 'defender', 'attacker_card', 'defender_card', 'result', 'timestamp')
    list_filter = ('result', 'timestamp')
    search_fields = ('attacker__username', 'defender__username')
    readonly_fields = ('result', 'timestamp')

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('number', 'game', 'owner')
    list_filter = ('game', 'owner')
    search_fields = ('owner__username',)

@admin.register(GameStatus)
class GameStatusAdmin(admin.ModelAdmin):
    list_display = ('game', 'status')
    list_filter = ('status',)
    search_fields = ('game__attacker__username', 'game__defender__username')

@admin.register(CardSelection)
class CardSelectionAdmin(admin.ModelAdmin):
    list_display = ('game', 'user', 'selected_card')
    list_filter = ('game', 'user')
    search_fields = ('user__username',)
