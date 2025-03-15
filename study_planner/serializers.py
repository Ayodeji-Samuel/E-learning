from rest_framework import serializers
from .models import Course, Commitment, StudySession, CourseProgress, Achievement, UserAchievement, UserPreferences

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'difficulty', 'priority', 'total_study_hours', 'deadline', 'created_at']

class CommitmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commitment
        fields = ['id', 'title', 'start_time', 'end_time', 'is_recurring', 'recurrence', 'notes']

class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = ['id', 'course', 'start_time', 'end_time', 'is_completed', 'notes']
        
        
class CourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProgress
        fields = ['id', 'course', 'hours_studied', 'last_studied']
        

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'type', 'threshold']
        

class UserAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAchievement
        fields = ['id', 'user', 'achievement', 'date_earned']
        
class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ['id', 'user', 'daily_study_limit', 'preferred_study_times', 'break_interval', 'break_duration']
        

