from rest_framework import viewsets, permissions
from .models import Course, Commitment, StudySession, CourseProgress, Achievement, UserAchievement, UserPreferences
from .serializers import CourseSerializer, CommitmentSerializer, StudySessionSerializer, CourseProgressSerializer, AchievementSerializer, UserAchievementSerializer, UserPreferencesSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class CommitmentViewSet(viewsets.ModelViewSet):
    queryset = Commitment.objects.all()
    serializer_class = CommitmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class StudySessionViewSet(viewsets.ModelViewSet):
    queryset = StudySession.objects.all()
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

# Repeat for other models (CourseProgress, Achievement, UserAchievement, UserPreferences)