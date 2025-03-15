#trivia_game/models.py

from django.db import models
from django.core.validators import MinValueValidator
#from eduPathCare.models import User  # Import your existing User model
from django.conf import settings
import random
from django.utils import timezone
from django.db.models import F

class Category(models.Model):
    """
    Represents a category for trivia questions (e.g., Sports, Math, Biology, History).
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class DifficultyLevel(models.Model):
    """
    Represents the difficulty levels for trivia questions and their corresponding coin prices.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, unique=True)
    price = models.PositiveIntegerField(help_text="Coins required to play this difficulty level.")

    def __str__(self):
        return f"{self.get_difficulty_display()} - {self.price} coins"

    class Meta:
        verbose_name = "Difficulty Level"
        verbose_name_plural = "Difficulty Levels"



class CoinReward(models.Model):
    """
    Represents the coin rewards for each question based on difficulty level.
    """
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)
    rewards = models.JSONField(
        default=list,
        help_text="A list of coin rewards for each question (e.g., [10, 20, 30, ...])."
    )

    def __str__(self):
        return f"{self.difficulty.get_difficulty_display()} Rewards"

    class Meta:
        verbose_name = "Coin Reward"
        verbose_name_plural = "Coin Rewards"


class Question(models.Model):
    """
    Represents a trivia question with its category, difficulty, and answers.
    """
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(help_text="The question text.")
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)
    correct_answer = models.CharField(max_length=255, help_text="The correct answer to the question.")
    wrong_answer1 = models.CharField(max_length=255, help_text="First wrong answer.")
    wrong_answer2 = models.CharField(max_length=255, help_text="Second wrong answer.")
    wrong_answer3 = models.CharField(max_length=255, help_text="Third wrong answer.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text} ({self.difficulty.get_difficulty_display()})"

    def get_shuffled_answers(self):
        """
        Returns a shuffled list of all answers (correct and wrong) for the question.
        """
        answers = [self.correct_answer, self.wrong_answer1, self.wrong_answer2, self.wrong_answer3]
        random.shuffle(answers)
        return answers


class GameSession(models.Model):
    """
    Represents a user's game session, tracking progress, score, and status.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_sessions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    current_question = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    score = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    questions = models.ManyToManyField(Question, through='GameSessionQuestion')

    def __str__(self):
        return f"Session {self.id} by {self.user.username}"

    def deduct_coins(self):
        """
        Deducts the coins from the user's account based on the selected difficulty level.
        """
        if self.difficulty:
            self.user.coins -= self.difficulty.price
            self.user.save()

    def get_coin_reward_for_current_question(self):
        """
        Returns the coin reward for the current question based on difficulty.
        """
        coin_reward = CoinReward.objects.get(difficulty=self.difficulty)
        return coin_reward.rewards[self.current_question - 1]

    def end_session(self):
        """
        Marks the session as completed and updates the end time.
        """
        self.is_completed = True
        self.end_time = timezone.now()
        self.save()

    def get_coin_reward_for_question(self, question_number):
        """
        Returns the coin reward for a specific question number.
        """
        coin_reward = CoinReward.objects.get(difficulty=self.difficulty)
        return coin_reward.rewards[question_number - 1]

    # def update_score(self, is_correct):
    #     """
    #     Updates the score based on whether the user answered correctly.
    #     If the user reaches the 10th question, the score is set to the reward for the 10th question.
    #     """
    #     if is_correct:
    #         if self.current_question == 10:
    #             # If it's the 10th question, set the score to the reward for the 10th question
    #             coin_reward = self.get_coin_reward_for_question(10)
    #             self.score = coin_reward
    #             #self.user.coins = F('coins') + coin_reward  # Add coins to the user's balance
    #             self.user.save()
    #             self.end_session()  # End the session after the 10th question
    #         else:
    #             # For questions 1-9, just move to the next question without updating the score
    #             self.current_question += 1
    #     else:
    #         # If the answer is wrong, end the game and set the score to 0
    #         self.score = 0
    #         self.end_session()
    #     self.save()
    
    def update_score(self, is_correct):
        """
        Updates the score based on whether the user answered correctly.
        If the user reaches the 10th question, the score is set to the reward for the 10th question.
        """
        if is_correct:
            if self.current_question == 10:
                # If it's the 10th question, set the score to the reward for the 10th question
                coin_reward = self.get_coin_reward_for_question(10)
                self.score = coin_reward
                #self.user.coins = F('coins') + coin_reward  # Add coins to the user's balance
                self.user.save()
                self.end_session()  # End the session after the 10th question
            else:
                # For questions 1-9, just move to the next question without updating the score
                self.current_question += 1
        else:
            # If the answer is wrong, end the game and set the score to 0
            self.score = 0
            self.end_session()
        self.save()
        
    


class GameSessionQuestion(models.Model):
    """
    Represents the relationship between a GameSession and a Question,
    including the user's answer and whether it was correct.
    """
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=255, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.game_session.id} - {self.question.text}"

    class Meta:
        unique_together = ('game_session', 'question')

