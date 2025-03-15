#trivia_game/urls.py

from django.urls import path
from .views import HomeView, PlayGameView, LeaderboardView, HandleDecisionView
from .views_admin import create_category, edit_category, delete_category, create_difficulty_level, edit_difficulty_level, delete_difficulty_level, create_coin_reward, edit_coin_reward, delete_coin_reward

app_name = 'trivia_game'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('play/<int:session_id>/', PlayGameView.as_view(), name='play_game'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('play/<int:session_id>/decision/', HandleDecisionView.as_view(), name='handle_decision'),
    
    path('admin/categories/create/', create_category, name='create_category'),
    path('admin/categories/edit/<int:category_id>/', edit_category, name='edit_category'),
    path('admin/categories/delete/<int:category_id>/', delete_category, name='delete_category'),
    path('admin/difficulty-levels/create/', create_difficulty_level, name='create_difficulty_level'),
    path('admin/difficulty-levels/edit/<int:difficulty_level_id>/', edit_difficulty_level, name='edit_difficulty_level'),
    path('admin/difficulty-levels/delete/<int:difficulty_level_id>/', delete_difficulty_level, name='delete_difficulty_level'),
    path('admin/coin-rewards/create/', create_coin_reward, name='create_coin_reward'),
    path('admin/coin-rewards/edit/<int:coin_reward_id>/', edit_coin_reward, name='edit_coin_reward'),
    path('admin/coin-rewards/delete/<int:coin_reward_id>/', delete_coin_reward, name='delete_coin_reward'),
]