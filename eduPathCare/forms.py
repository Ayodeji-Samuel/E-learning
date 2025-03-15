#eduPathCare/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from .models import User, Subject, Section, Subsection, FinalExam, Quiz
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget

# Sign Up Form
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'profile_picture', 'bio')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Enter your username',
                'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email',
                'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Enter your password',
                'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': 'Confirm your password',
                'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Enter your first name',
                'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Enter your last name',
                'class': 'mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-gray-900 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
        }        

# Password Reset Form
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(required=True)

    class Meta:
        fields = ('email',)



class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_name', 'description', 'price', 'featured']
        widgets = {
            'subject_name': forms.TextInput(attrs={
                'placeholder': 'Subject Name', 
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
            'description': SummernoteWidget(),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-blue-600'
            }),
        }

# Section Form
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['section_name', 'section_order', 'text_content', 'image_content']
        
        widgets = {
            'text_content': SummernoteWidget(),
            'image_content': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
        }


# eduPathCare/forms.py

class SubsectionForm(forms.ModelForm):
    class Meta:
        model = Subsection
        fields = ['subsection_name', 'subsection_order', 'text_content', 'image_content']
        widgets = {
            'text_content': SummernoteWidget(),
            'image_content': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300'
            }),
        }
#============================================================================================

# forms.py
from .models import Question

class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super(QuizForm, self).__init__(*args, **kwargs)
        
        for question in questions:
            self.fields[f'question_{question.question_id}'] = forms.ChoiceField(
                choices=[
                    ('a', question.option_a),
                    ('b', question.option_b),
                    ('c', question.option_c),
                    ('d', question.option_d),
                ],
                widget=forms.RadioSelect,
                label=question.question_text
            )
            


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'explanation_a', 'explanation_b', 'explanation_c', 'explanation_d']
        widgets = {
            'question_text': SummernoteWidget(),
            'option_a': forms.TextInput(attrs={'placeholder': 'Option A', 'class': 'form-control'}), 
            'option_b': forms.TextInput(attrs={'placeholder': 'Option B', 'class': 'form-control'}),
            'option_c': forms.TextInput(attrs={'placeholder': 'Option C', 'class': 'form-control'}),
            'option_d': forms.TextInput(attrs={'placeholder': 'Option D', 'class': 'form-control'}),
            'correct_option': forms.Select(choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')], attrs={'class': 'form-control'}),
            'explanation_a': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'explanation_b': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'explanation_c': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'explanation_d': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
        

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Select a CSV file')
    
    
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'first_name', 'last_name', 'profile_picture', 'bio', 'coins']
        

# eduPathCare/forms.py

class AdminQuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['user', 'subject', 'section', 'total_score', 'attempts_count', 'completed_at', 'time_spent']
        widgets = {
            'completed_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'time_spent': forms.NumberInput(attrs={'class': 'form-control'}),  # Time in seconds
        }


# eduPathCare/forms.py

class FinalExamForm(forms.ModelForm):
    class Meta:
        model = FinalExam
        fields = ['user', 'subject', 'total_score', 'attempts_count', 'completed_at', 'time_spent']
        widgets = {
            'completed_at': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'time_spent': forms.NumberInput(attrs={'class': 'form-control'}),  # Time in seconds
        }