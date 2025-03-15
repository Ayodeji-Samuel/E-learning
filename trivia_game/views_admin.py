from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Category, Question, CoinReward, DifficultyLevel
from .forms import CategoryForm, DifficultyLevelForm, CoinRewardForm

# trivia_game/views.py

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    return render(request, 'admin/create_category.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('manage_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin/edit_category.html', {'form': form, 'category': category})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('manage_categories')


#========================DIFFICULTY LEVELS========================
# trivia_game/views.py

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_difficulty_level(request):
    if request.method == 'POST':
        form = DifficultyLevelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Difficulty Level created successfully.')
            return redirect('manage_difficulty_levels')
    else:
        form = DifficultyLevelForm()
    return render(request, 'admin/create_difficulty_level.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_difficulty_level(request, difficulty_level_id):
    difficulty_level = get_object_or_404(DifficultyLevel, id=difficulty_level_id)
    if request.method == 'POST':
        form = DifficultyLevelForm(request.POST, instance=difficulty_level)
        if form.is_valid():
            form.save()
            messages.success(request, 'Difficulty Level updated successfully.')
            return redirect('manage_difficulty_levels')
    else:
        form = DifficultyLevelForm(instance=difficulty_level)
    return render(request, 'admin/edit_difficulty_level.html', {'form': form, 'difficulty_level': difficulty_level})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_difficulty_level(request, difficulty_level_id):
    difficulty_level = get_object_or_404(DifficultyLevel, id=difficulty_level_id)
    difficulty_level.delete()
    messages.success(request, 'Difficulty Level deleted successfully.')
    return redirect('manage_difficulty_levels')

#============================Coin Rewards============================
# trivia_game/views.py

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_coin_reward(request):
    if request.method == 'POST':
        form = CoinRewardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coin Reward created successfully.')
            return redirect('manage_coin_rewards')
    else:
        form = CoinRewardForm()
    return render(request, 'admin/create_coin_reward.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_coin_reward(request, coin_reward_id):
    coin_reward = get_object_or_404(CoinReward, id=coin_reward_id)
    if request.method == 'POST':
        form = CoinRewardForm(request.POST, instance=coin_reward)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coin Reward updated successfully.')
            return redirect('manage_coin_rewards')
    else:
        form = CoinRewardForm(instance=coin_reward)
    return render(request, 'admin/edit_coin_reward.html', {'form': form, 'coin_reward': coin_reward})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_coin_reward(request, coin_reward_id):
    coin_reward = get_object_or_404(CoinReward, id=coin_reward_id)
    coin_reward.delete()
    messages.success(request, 'Coin Reward deleted successfully.')
    return redirect('manage_coin_rewards')

