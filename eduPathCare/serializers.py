# serializers.py
from rest_framework import serializers
from .models import User, Subject, Section, Question, Quiz, UserProgress

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'role', 'first_name', 'last_name', 'profile_picture', 'bio']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['subject_id', 'subject_name', 'description', 'featured']

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['section_id', 'subject', 'section_name', 'section_order', 'text_content', 'image_content']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['question_id', 'section', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'explanation_a', 'explanation_b', 'explanation_c', 'explanation_d']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['quiz_id', 'user', 'subject', 'section', 'total_score', 'attempts_count', 'completed_at']

class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = ['progress_id', 'user', 'subject', 'completed_sections', 'total_score', 'created_at', 'updated_at']