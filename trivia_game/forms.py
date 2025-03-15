#trivia_game/forms.py

from django import forms
from .models import Category, DifficultyLevel, CoinReward

class StartGameForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Select Category",
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded'})
    )
    difficulty = forms.ChoiceField(
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        label="Select Difficulty",
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded'})
    )
    
# trivia_game/forms.py

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
        }
        
# trivia_game/forms.py

class DifficultyLevelForm(forms.ModelForm):
    class Meta:
        model = DifficultyLevel
        fields = ['difficulty', 'price']
        widgets = {
            'difficulty': forms.Select(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
        }
        
# trivia_game/forms.py

class CoinRewardForm(forms.ModelForm):
    class Meta:
        model = CoinReward
        fields = ['difficulty', 'rewards']
        widgets = {
            'difficulty': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
            'rewards': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300',
                'placeholder': 'Enter rewards as a JSON list (e.g., [10, 20, 30])'
            }),
        }
        
