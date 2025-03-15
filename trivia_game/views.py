#trivia_game/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.db.models import F
from .models import Category, Question, GameSession, GameSessionQuestion, CoinReward, DifficultyLevel
from .forms import StartGameForm
import random

class HomeView(View):
    """
    Home view to display categories and start a new game.
    """
    def get(self, request):
        form = StartGameForm()
        categories = Category.objects.all()
        return render(request, 'trivia_game/home.html', {'form': form, 'categories': categories})

    def post(self, request):
        form = StartGameForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            difficulty_str = form.cleaned_data['difficulty']
            
            difficulty = DifficultyLevel.objects.get(difficulty=difficulty_str)
            
            # Check if the user has enough coins
            if request.user.coins < difficulty.price:
                messages.error(request, "You do not have enough coins to play this difficulty level.")
                return redirect('trivia_game:home')
            
            questions = Question.objects.filter(category=category, difficulty=difficulty).order_by('?')[:10]
            
            if questions.count() < 10:
                messages.error(request, "Not enough questions for this category and difficulty.")
                return redirect('trivia_game:home')

            game_session = GameSession.objects.create(
                user=request.user,
                category=category,
                difficulty=difficulty,
            )
            game_session.deduct_coins()  # Deduct coins from the user's account
            game_session.questions.set(questions)
            return redirect('trivia_game:play_game', session_id=game_session.id)
        return render(request, 'trivia_game/home.html', {'form': form})



class PlayGameView(View):
    """
    View to handle the game session and user answers.
    """
    def get(self, request, session_id):
        game_session = get_object_or_404(GameSession, id=session_id, user=request.user)
        if game_session.is_completed:
            messages.info(request, "This game session has already ended.")
            return redirect('trivia_game:home')

        current_question = game_session.questions.all()[game_session.current_question - 1]
        coin_reward = game_session.get_coin_reward_for_current_question()
        shuffled_answers = current_question.get_shuffled_answers()

        # Preprocess question rewards and text
        question_rewards = []
        questions = list(game_session.questions.all())  # Convert queryset to list
        for i, question in enumerate(questions, start=1):
            question_rewards.append({
                'number': i,
                'reward': game_session.get_coin_reward_for_question(i),
                'text': question.text  # Add question text directly
            })

        return render(request, 'trivia_game/game.html', {
            'game_session': game_session,
            'question': current_question,
            'coin_reward': coin_reward,
            'answers': shuffled_answers,
            'question_rewards': question_rewards,  # Pass preprocessed data
        })

    def post(self, request, session_id):
        game_session = get_object_or_404(GameSession, id=session_id, user=request.user)
        
        current_question = game_session.questions.all()[game_session.current_question - 1]
        user_answer = request.POST.get('answer')

        is_correct = user_answer == current_question.correct_answer

        if game_session.current_question == 5 and is_correct:
            # Ask the user if they want to take the coins or continue
            return render(request, 'trivia_game/decision.html', {
                'game_session': game_session,
                'coin_reward': game_session.get_coin_reward_for_question(5),
            })

        game_session.update_score(is_correct)

        if is_correct and game_session.current_question == 11:
            messages.success(request, f"Congratulations! You won {game_session.score} coins.")
            return redirect('trivia_game:leaderboard')

        if not is_correct:
            messages.error(request, "Incorrect answer. Game over!")
            return redirect('trivia_game:leaderboard')

        if game_session.is_completed:
            messages.info(request, "This game session has already ended.")
            return redirect('trivia_game:home')

        return redirect('trivia_game:play_game', session_id=game_session.id)
        

class HandleDecisionView(View):
    """
    View to handle the user's decision after the fifth question.
    """
    def post(self, request, session_id):
        game_session = get_object_or_404(GameSession, id=session_id, user=request.user)
        decision = request.POST.get('decision')

        if decision == 'take_coins':
            # Add the fifth question coins to the score and end the game
            fifth_question_reward = game_session.get_coin_reward_for_question(5)
            game_session.score = fifth_question_reward  # Add reward to the score field
            game_session.end_session()
            messages.success(request, f"You took {fifth_question_reward} coins. Game over!")
            return redirect('trivia_game:leaderboard')
        elif decision == 'continue':
            # Continue with the remaining questions
            game_session.current_question += 1
            game_session.save()
            return redirect('trivia_game:play_game', session_id=game_session.id)











    
    
    
from django.db.models import Sum

class LeaderboardView(View):
    """
    View to display the leaderboard with cumulative scores for all users.
    """
    def get(self, request):
        # Aggregate the total score for each user across all game sessions
        leaderboard = (
            GameSession.objects
            .values('user__username')  # Group by username
            .annotate(total_score=Sum('score'))  # Sum the scores for each user
            .order_by('-total_score')  # Order by total score in descending order
        )

        return render(request, 'trivia_game/leaderboard.html', {'leaderboard': leaderboard})