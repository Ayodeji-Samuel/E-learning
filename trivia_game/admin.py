from django.contrib import admin
from .models import Category, Question, GameSession, GameSessionQuestion, CoinReward, DifficultyLevel

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'difficulty', 'created_at')
    list_filter = ('category', 'difficulty')
    search_fields = ('text',)

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'difficulty', 'start_time', 'is_completed', 'score')
    list_filter = ('difficulty', 'is_completed')
    search_fields = ('user__username',)

@admin.register(GameSessionQuestion)
class GameSessionQuestionAdmin(admin.ModelAdmin):
    list_display = ('game_session', 'question', 'is_correct', 'answered_at')
    list_filter = ('is_correct',)


@admin.register(CoinReward)
class CoinRewardAdmin(admin.ModelAdmin):
    list_display = ('difficulty', 'rewards')
    list_editable = ('rewards',)  # Allows editing rewards directly from the list view
    
@admin.register(DifficultyLevel)
class DifficultyLevelAdmin(admin.ModelAdmin):
    list_display = ('difficulty', 'price')
    list_editable = ('price',)